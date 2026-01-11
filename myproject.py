'''
Đề bài chi tiết:
 
Xây dựng 01 trang web trực quan hóa dữ liệu (phân tích mô tả) cho bảng dữ liệu tùy chọn. Với các thành phần: 
1.	Ứng dụng Web Server lưu dữ liệu
2.	Web Client để hiển thị dữ liệu
3.	Hệ thống Web Server được phát triển bới Flask, xử lý các mẫu dữ liệu và cung cấp các truy vấn cho phía
    Web Client người dùng để lấy được các dữ liệu mong muốn

-> Có thể sử dụng AI để hỗ trợ quá trình xây dựng.

->Các nội dung hiển thị tùy thuộc vào học viên quyết định. 
'''
from flask import Flask, jsonify, request, render_template  # Import Flask core and JSON helpers
from flask_cors import CORS  # Import the Flask-CORS extension
from pathlib import Path  # Import Path for file system 
import os  # Import os for environment variable handling
import json  # Import json for JSON handling
import subprocess  # Import subprocess for running shell commands
from dotenv import load_dotenv  # Import load_dotenv for environment variable handling
load_dotenv()  # Load environment variables from .env file



# Initialize the Flask application
app = Flask(__name__, static_folder='src')
'''Create a Flask instance with static_folder = 'src' instead of using static (default)'''


# Apply CORS to the app to allow frontend requests instead of using the CORSMiddleware which is equivalent.
CORS(app)

ai_path = Path('./Scraper_data/data/air_quality.json')  # Define path to the JSON file
his_path = Path('./Scraper_data/data/history_air_quality.json')  # Defile path to the history JSON file

# Create a function to standardize various forms of Saigon/HCMC and Kuala Lumpur to a consistency name
def normalize_city_name(city_input):
    # Clean the input: remove extra whitespace and convert to lowercase for comparison
    clean_input = str(city_input).strip().lower()
    
    # Define acceptable variations
    saigon_variants = ["saigon", "ho chi minh", "ho chi minh city", "hcmc", "tphcm", "tp.hcm", "hcm" ]

    Kuala_Lumpur_variants = ["kuala lumpur", "kuala lumpur city", "kl" ]

    # Check if the input is in the list of variants
    if clean_input in saigon_variants:
        return "Saigon"
    
    elif clean_input in Kuala_Lumpur_variants:
        return "Kuala Lumpur"
    
    else:
        # Return the original title-cased name if it's a different city
        return city_input.title()

# Use GET Method to make API Home page
@app.route('/', methods=['GET'])
def home():
    # return jsonify ('Welcome to my Final Project - Air Quality Monitoring for Ho Chi Minh and Hanoi!!!')
    return render_template('index.html') # Display this website as a home page

# Use GET Method to make API Endpoint 'api/current' for current dataset of all cities (Ho Chi Minh, Ha Noi and Perth)
@app.route('/api/current', methods=['GET'])
def current_aqi():
    try:
        with open(ai_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
            return jsonify({"status": "success", "data": data})
    except Exception as e:
            return jsonify({"status": "error", "message": str(e)}), 500
    
# Use GET Method to make API Endpoint 'api/history' for history dataset of all cities
@app.route('/api/history', methods=['GET'])
def history_all():
    try:
        with open (his_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
            return jsonify({"status": "success", "data": data})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# Use GET Method to make API Endpoint 'api/history/<city>' for history data of a specific city (Ho Chi Minh, Ha Noi and Perth)
@app.route('/api/history/<city>', methods=['GET'])
def history_aqi(city):
    try:
        # Normalize the city name (e.g., HCMC -> Saigon)
        normalized_city = normalize_city_name(city) 
        
        # Open and load the JSON file directly
        with open(his_path, 'r', encoding='utf-8') as file:
            all_data = json.load(file)
        
        # Filter the list of dictionaries for the matching city
        city_data = [record for record in all_data if record.get('City', '').lower() == normalized_city.lower()]
        
        if not city_data:
            return jsonify({"status": "error", "message": f"No data found for city: {city}" }), 404
            
        return jsonify({"status": "success", "city": normalized_city, "data": city_data })
        
    except Exception as e:
        return jsonify({"status": "error", "message": str(e) }), 500
    
    
''' Implement CRUD (POST, PUT, DELETE).'''

# Use POST Methods to create an endpoints for user (frontend) to input a new dataset of a city - CREATE NEW DATA
# Create a helper function to get the next ID for POST
def get_next_id(data):
    return max([item.get('id', 0) for item in data], default=0) + 1

@app.route('/api/history', methods=['POST'])
def add_history():
    new_data = request.get_json()  # Get data from frontend
    
    with open(his_path, 'r+') as file:  # Open file in read and write mode
        data = json.load(file)
        # Auto-assign ID
        new_data['id'] = get_next_id(data)
        data.append(new_data)
        
        file.seek(0)  # Move the file pointer to the beginning
        json.dump(data, file, indent=4)  # Write the updated data back to the file
        file.truncate()  # Truncate the file to the current position
        
    return jsonify({"status": "success", "message": "Record added", "id": new_data['id']}), 201

# Use PUT Methods to create an endpoints for user (frontend) to update data of a city = UPDATE DATA
@app.route('/api/history/<int:record_id>', methods=['PUT'])
def update_history(record_id):
    updated_values = request.get_json()  # Get data from frontend
    
    with open(his_path, 'r+') as file:  # Open file in read and write mode
        data = json.load(file)
        # Find the record by ID and update it
        found = False
        for record in data:
            if record['id'] == record_id:
                record.update(updated_values)
                found = True
                break
        
        if not found:
            return jsonify({"status": "error", "message": "Record not found"}), 404
            
        file.seek(0)  # Move the file pointer to the beginning
        json.dump(data, file, indent=4)  # Write the updated data back to the file
        file.truncate()  # Truncate the file to the current position
               
    return jsonify({"status": "success", "message": f"Record {record_id} updated"})

# Use DELETE Methods to create an endpoints for user (frontend) to delete data of a city in accordence with IDs
@app.route('/api/history/<int:record_id>', methods=['DELETE'])
def delete_record(record_id):
    with open(his_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Filter out the record
    new_data = [record for record in data if record.get('id') != record_id]
    
    if len(new_data) == len(data):
        return jsonify({"status": "error", "message": "ID not found"}), 404
        
    with open(his_path, 'w', encoding='utf-8') as f:
        ''' Write the updated data back to the file, overwriting the original file '''
        json.dump(new_data, f, indent=4)
        
    return jsonify({"status": "success", "message": f"Record {record_id} deleted"})

# Create an endpoint to run the scraper (scraping dataset) when user press "Refresh Button" from web client (frontend)
@app.route('/api/scrape', methods=['POST'])
def trigger_scrape():
    try:
        # Define where the scraper and JSON files live = Path: Scraper_data/json/
        folder_path = os.path.join("Scraper_data")
        scraper_file = "scraper.py"
        
        # Check if the script exists
        script_path = os.path.join(folder_path, scraper_file)
        if not os.path.exists(script_path):
            return jsonify({"status": "error", "message": f"Scraper not found at {script_path}"}), 404

        # RUN THE SCRAPER
        # 'cwd=folder_path' is critical! It forces the script to "act" as if it is running from inside the 'json' folder. 
        # This makes Path("./air_quality.json") point to the correct file (inside the scraper.py script)
        subprocess.run(["python", scraper_file], cwd=folder_path, check=True) # cwd = Current Working Directory
        
        return jsonify({
            "status": "success", 
            "message": "Scrape completed! JSON files in Scraper_data/json/ have been updated."
        })

    except subprocess.CalledProcessError as e:
        return jsonify({"status": "error", "message": f"Scraper crashed: {str(e)}"}), 500
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# =================================================================================
# Connect API Endpoints by using JavaScript (JS) + HTML for Web Client to connect the Flask Server
'''
By writing a prompt for AI (Gemini) to implement as follows: “ Please use JavaScript and CSS (priority to use Tailwind CSS for styling), write in the html file to
connect and display (visualize) data from the API to the screen with the API endpoints as follows: http://127.0.0.1:8000/api/current for current dataset of all cities
and http://127.0.0.1:8000/api/history for history dataset of all cities”

The index.html was then created and stored in the final_project/templates folder to be displayed on the frontend web client as a home page (the home page API endpoint).
'''

# Start the Flask server
if __name__ == '__main__': 
    app.run(debug=True, port=os.getenv('PORT', 8000)) # Get PORT from the environment file .env