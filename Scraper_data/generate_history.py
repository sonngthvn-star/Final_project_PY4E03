import json # thư viện xử lý JSON
import pandas as pd # thư viện xử lý dữ liệu
import numpy as np # thư viện toán học
from datetime import datetime, timedelta # thư viện xử lý thời gian

# Tao lớp (class) để tạo dữ liệu lịch sử giả lập
class AQI_history:
    def __init__(self, file_path):
        self.file_path = file_path

    #   Hàm khởi tạo dữ liệu giả lập - Mocking up history dataset
    def generate_history_aqi(self, day):
        # Khởi tạo các tham số giả lập dựa trên thống kê thực tế để tính toán các thông số: AQI, PM10 và PM2.5
        # Theo thống kê thực tế, lấy PM10 = 1.6 cho các thành phố bụi mịn cao (VN), PM10 = 1.3 cho thành phố sạch hơn (Australia)

        cities = [
            {"name": "Hanoi", "country": "Vietnam", "aqi_range": (120, 190), "pm10_mult": 1.6},
            {"name": "Saigon", "country": "Vietnam", "aqi_range": (70, 130), "pm10_mult": 1.6},
            {"name": "Perth", "country": "Australia", "aqi_range": (10, 40), "pm10_mult": 1.3},
            {"name": "Bangkok", "country": "Thailand", "aqi_range": (100, 160), "pm10_mult": 1.6},
            {"name": "Singapore", "country": "Singapore", "aqi_range": (40, 70), "pm10_mult": 1.4},
            {"name": "Kuala Lumpur", "country": "Malaysia", "aqi_range": (50, 90), "pm10_mult": 1.5},
            {"name": "Jakarta", "country": "Indonesia", "aqi_range": (120, 170), "pm10_mult": 1.6},
            {"name": "Manila", "country": "Philippines", "aqi_range": (70, 120), "pm10_mult": 1.6},
            {"name": "Beijing", "country": "China", "aqi_range": (50, 200), "pm10_mult": 1.6},
            {"name": "Shanghai", "country": "China", "aqi_range": (50, 180), "pm10_mult": 1.6}
        ]

        data_list = [] 
        end_date = datetime.now()
        record_id = 1 # Bắt đầu chỉ số IDs = 1 

        for i in range(day): 
            current_date = (end_date - timedelta(days=i)).strftime("%Y-%m-%d") 
            for city in cities:
                # Tạo giá trị ngẫu nhiên AQI theo thống kê thực cho các thành phố

                aqi = np.random.randint(city["aqi_range"][0], city["aqi_range"][1])
                                         
                # Tính PM2.5 (PM2.5 = 80% AQI)
                pm25 = round(aqi * 0.8, 1)
                
                # Tính PM10 dựa trên tỷ lệ thực tế
                pm10 = round(pm25 * city["pm10_mult"], 1)

                data_list.append({
                    "id": record_id,
                    "City": city["name"],
                    "Country": city["country"],
                    "AQI": aqi,
                    "PM25": pm25,
                    "PM10": pm10,
                    "Date": current_date
                })
                record_id += 1

        # Lưu data vào file json
        with open(self.file_path, 'w', encoding='utf-8') as f:
            json.dump(data_list, f, indent=4, ensure_ascii=False)
      
        print(f"Đã tạo xong file lịch sử giả lập: {self.file_path}!!!")
    
