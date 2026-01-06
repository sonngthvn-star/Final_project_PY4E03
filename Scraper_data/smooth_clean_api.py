import pandas as pd  # Thư viện dùng để đọc, ghi và xử lý dữ liệu bảng (CSV/DataFrame)
import numpy as np  # Thư viện hỗ trợ tính toán số học và tạo số ngẫu nhiên
from datetime import datetime, timedelta  # Thư viện xử lý ngày tháng và khoảng thời gian

class AirQualityCleaner:  # Định nghĩa lớp để quản lý các hàm làm sạch dữ liệu
    def __init__(self, file_path):  # Hàm khởi tạo nhận vào đường dẫn file CSV
        self.file_path = file_path  # Lưu đường dẫn file vào biến toàn cục của lớp

    def smooth_air_quality_data(self):  # Hàm chính để thực hiện việc chuẩn hóa dữ liệu
        # 1. Đọc dữ liệu từ file json hiện tại (scraped dataset from website: https://aqicn.org/api/) vào bộ nhớ (DataFrame)
        df = pd.read_json(self.file_path) 
        
        # Lấy thời gian UTC hiện tại và cộng thêm 7 giờ để đồng bộ với múi giờ Việt Nam (ICT)
        now_ict = datetime.utcnow() + timedelta(hours=7)
        # Chuyển đổi thời gian thành chuỗi theo định dạng Năm-Tháng-Ngày Giờ:Phút:Giây
        now_str = now_ict.strftime('%Y-%m-%d %H:%M:%S')

        # Định nghĩa các ngưỡng kiểm soát và dải giá trị thực tế cho từng thành phố
        thresholds = {
            'Hanoi': {
                'aqi_min': 50,           # AQI tối thiểu (nếu thấp hơn là lỗi sensor)
                'temp_min': 10,          # Nhiệt độ tối thiểu (mùa đông Hà Nội)
                'pm25_min_ratio': 0.6,   # PM2.5 phải chiếm ít nhất 60% chỉ số AQI
                'aqi_range': (150, 180), # Dải AQI ngẫu nhiên để bù đắp khi dữ liệu mất
                'temp_range': (14.0, 18.0) # Dải nhiệt độ ngẫu nhiên để bù đắp khi dữ liệu mất
            },
            'Saigon': {
                'aqi_min': 40, 
                'temp_min': 20, 
                'pm25_min_ratio': 0.6,
                'aqi_range': (80, 110), 
                'temp_range': (28.0, 33.0)
            },
            'Perth': {
                'aqi_min': 5, 
                'temp_min': 5, 
                'pm25_min_ratio': 0.4,   # Úc không khí sạch nên tỷ lệ bụi mịn thấp hơn
                'aqi_range': (10, 35), 
                'temp_range': (15.0, 25.0)
            },

            'Bangkok': {
                'aqi_min': 40,
                'temp_min': 20,
                'pm25_min_ratio': 0.6,
                'aqi_range': (100, 160),
                'temp_range': (25.0, 32.0)
            },

            'Singapore': {
                'aqi_min': 20,
                'temp_min': 23,
                'pm25_min_ratio': 0.5,
                'aqi_range': (40, 70),
                'temp_range': (26.0, 31.0)
            },

            'Kuala Lumpur': {
                'aqi_min': 30,
                'temp_min': 22,
                'pm25_min_ratio': 0.5,
                'aqi_range': (50, 90),
                'temp_range': (25.0, 32.0)
            },

            'Jakarta': {
                'aqi_min': 50,
                'temp_min': 22,
                'pm25_min_ratio': 0.6,
                'aqi_range': (120, 170),
                'temp_range': (26.0, 33.0)
            },

            'Manila': {
                'aqi_min': 40,
                'temp_min': 22,
                'pm25_min_ratio': 0.6,
                'aqi_range': (70, 120),
                'temp_range': (26.0, 32.0)
            },

            'Beijing': {
                'aqi_min': 30,
                'temp_min': -10,
                'pm25_min_ratio': 0.7,
                'aqi_range': (50, 200),
                'temp_range': (-5.0, 5.0)
            },

            'Shanghai': {
                'aqi_min': 30,
                'temp_min': 3,
                'pm25_min_ratio': 0.6,
                'aqi_range': (50, 180),
                'temp_range': (3.0, 33.0)
            }

        }

        def process_row(row):  # Hàm con để xử lý logic cho từng hàng dữ liệu
            city = row['City']  # Lấy tên thành phố ở hàng hiện tại
            
            # Ghi đè thời gian hiện tại (đã fix múi giờ) vào cột 'Time' cho mọi dòng
            row['Time'] = now_str
            
            if city in thresholds:  # Nếu thành phố nằm trong cấu hình kiểm soát
                t = thresholds[city]  # Lấy bộ thông số tương ứng của thành phố đó
                
                # Kiểm tra AQI: Nếu trống (NaN) hoặc quá thấp, tạo giá trị ngẫu nhiên hợp lý (dựa theo giá trị thực thống kê)
                if pd.isna(row['AQI']) or row['AQI'] < t['aqi_min']:
                    row['AQI'] = np.random.randint(t['aqi_range'][0], t['aqi_range'][1])
                
                # Kiểm tra Nhiệt độ: Nếu trống hoặc quá thấp, tạo nhiệt độ ngẫu nhiên trong dải
                if pd.isna(row['Temperature']) or row['Temperature'] < t['temp_min']:
                    row['Temperature'] = round(np.random.uniform(t['temp_range'][0], t['temp_range'][1]), 1)

                # Kiểm tra PM2.5: Nếu quá thấp so với AQI (lỗi phổ biến của sensor bụi)
                # Tính lại PM2.5 bằng 75% - 85% giá trị AQI hiện tại
                if pd.isna(row['PM25']) or row['PM25'] < (row['AQI'] * t['pm25_min_ratio']):
                    row['PM25'] = round(row['AQI'] * np.random.uniform(0.75, 0.85), 1)

                # Xác định tỷ lệ bụi thô (PM10) dựa trên quốc gia (Việt Nam thường có tỷ lệ cao hơn)
                ratio = 1.6 if row['Country'] == 'Vietnam' else 1.3

                # Đảm bảo PM10 luôn lớn hơn PM2.5 (vì PM10 bao gồm cả PM2.5 bên trong)
                if pd.isna(row['PM10']) or row['PM10'] <= row['PM25']:
                    row['PM10'] = round(row['PM25'] * ratio, 1)

            return row  # Trả về hàng dữ liệu sau khi đã được chỉnh sửa

        # Sử dụng hàm apply để chạy hàm process_row xuyên suốt toàn bộ các dòng của bảng
        df = df.apply(process_row, axis=1)

        # Lưu lại toàn bộ dữ liệu đã làm sạch đè lên file json cũ
        df.to_json(self.file_path, orient='records', index=4, force_ascii=False)

        # In thông báo trạng thái ra màn hình
        print(f"--- Đã hoành thành xử lý dữ liệu và lưu vào file '{self.file_path}' lúc: {now_str} ---")

        # Hiển thị bảng dữ liệu cuối cùng để người dùng kiểm tra nhanh
        print(df)
        
        return df  # Trả về kết quả cho mục đích sử dụng khác nếu cần

