'''
This script will perform functions as below:

1.  Scraping dataset for my final project from a Website API: https://aqicn.org/api/, by using Python requests to collect
    real-time Air Quality data from WAQI API with my token (b4fd2856b2c8d8bb8a4b456bd88f8ae7366c753c) getting from web API:
    https://aqicn.org/data-platform/token/

2.  The data will be saved as a CSV file for further analysis and visualization.
3.  Clean and manipulate the data to ensure quality and consistency.
4.  Generate simulated historical air quality data for Hanoi, Ho Chi Minh City, and Perth over the past 30 days for time series charting.

'''

import requests # library to make HTTP requests
import pandas as pd # library for data manipulation and analysis
import json # library to handle JSON data
import os # library to interact with the operating system
from pathlib import Path # library to handle file paths
from smooth_clean_api import AirQualityCleaner # library (class) to clean and smooth air quality data
from generate_history import AQI_history # library (class) to generate simulated historical air quality data


aq_path = Path("./data/air_quality.json") # Define path to save the scraped air quality data
his_path = Path("./data/history_air_quality.json") # Define path to save the simulated historical data

TOKEN = "b4fd2856b2c8d8bb8a4b456bd88f8ae7366c753c" # My token to access WAQI API

# List of backup stations to scrape data for each city (if one station fails or has invalid data, try the next one)
STATIONS_MAP = {
    "Hanoi": ["@8667", "@14731", "hanoi"],
    "Saigon": ["@8641", "@9137", "@13540", "saigon"],
    "Perth": ["@10811", "@10813", "perth"],
    "Bangkok": ["@8538", "@10373", "bangkok"],
    "Singapore": ["@5513", "@7109", "singapore"],
    "Kuala Lumpur": ["@10816", "@10817", "kuala lumpur"],
    "Jakarta": ["@10745", "@8674", "jakarta"],
    "Manila": ["@10842", "@10843", "manila"],
    "Beijing": ["@1437", "@3125", "beijing"],
    "Shanghai": ["@1451", "@1438", "shanghai"]

}

# Mapping cities to their respective countries for the CSV
COUNTRY_LOOKUP = {
    "Hanoi": "Vietnam",
    "Saigon": "Vietnam",
    "Perth": "Australia",
    "Bangkok": "Thailand",
    "Singapore": "Singapore",
    "Kuala Lumpur": "Malaysia",
    "Jakarta": "Indonesia",
    "Manila": "Philippines",
    "Beijing": "China",
    "Shanghai": "China"
}

# Create a function to get valid AQI data for a specifict city from its list of stations
def get_valid_data(city_name, station_list):
    for sid in station_list:
        url = f"https://api.waqi.info/feed/{sid}/?token={TOKEN}" # API endpoint for each station in the city (given by Gemini)
        try:
            res = requests.get(url).json() # Make a GET request to the API and parse the JSON response
            if res['status'] == 'ok':
                data = res['data']
                aqi = data.get('aqi')
                # Kiểm tra AQI phải là số dương và có dữ liệu thời gian
                if isinstance(aqi, (int, float)) and aqi > 0:
                    iaqi = data.get('iaqi', {})
                    return {
                        "City": city_name,
                        "Country": COUNTRY_LOOKUP.get(city_name, "Unknown"),
                        "AQI": aqi,
                        "PM25": iaqi.get('pm25', {}).get('v', 0),
                        "PM10": iaqi.get('pm10', {}).get('v', 0),
                        "Temperature": iaqi.get('t', {}).get('v', 0),
                        "Humidity": iaqi.get('h', {}).get('v', 0),
                        "Time": data.get('time', {}).get('s', "N/A")
                    }
        except:
            continue # if there is a connection or parsing error, try the next station
    return None # Return None if no valid data found for the city

#=========================
def save_with_ids(new_data_list, target_path):
    """Saves data as a proper JSON array and resets/overwrites the file every run"""

    processed_data = []  # Initialize an empty list to store processed records

    # Reset IDs: Start from 1 for the current batch of scraped data
    for i, record in enumerate(new_data_list, start=1):
        record['id'] = i
        processed_data.append(record)

    # Save as a clean JSON list, overwriting existing data in the json file
    with open(target_path, 'w', encoding='utf-8') as f:
        json.dump(processed_data, f, indent=4, ensure_ascii=False)

# EXECUTION LOGIC: Loop through each city and its stations to get the best available data
all_data = [] # Initialize an empty list to store dataset 

for city, sids in STATIONS_MAP.items():
    print(f"Checking best station for {city}...")
    result = get_valid_data(city, sids)
    if result:
        all_data.append(result) # Append valid data to the dataset

# Save dataset: This will now overwrite existing data stored in air_quality.json
print(f"Overwriting data with new IDs to {aq_path}...")
save_with_ids(all_data, aq_path) 

print('-' * 30)

# Clean and Smooth the fresh data
print(f'Commencing manipulation of {aq_path}...')
AirQualityCleaner(aq_path).smooth_air_quality_data() # Call AirQualityCleaner (class) to conduct tasks required


# Generate history data: Ensure this class also overwrites
print (f'Commence mocking a history dataset and save to file {his_path} ...')
AQI_history(his_path).generate_history_aqi(60)


