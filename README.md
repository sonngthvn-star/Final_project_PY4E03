Air Quality Monitoring Portal 🌍
    An end-to-end web application designed to track, analyze, and visualize real-time and historical air quality data (AQI, PM2.5, PM10) for major cities across Asia and Australia.

📌 Project Overview
    Developed for the PY4E03 course, this system utilizes a Python-based scraper to fetch live data from the WAQI (World Air Quality Index) API. The data is served through a Flask REST API and visualized on a modern, interactive dashboard featuring maps, charts, and data management capabilities.

Key Features:
    - Real-time Data Scraping: Automated fetching of AQI, PM2.5, and PM10 levels.

    - Interactive Dashboard: Built with Tailwind CSS and Chart.js for sleek, responsive data visualization.

    - Geospatial Mapping: Integrated Leaflet.js map to view air quality markers by city.

    - Historical Analysis: Simulated 30-day historical data generation for Hanoi, Saigon, and Perth.

    - CRUD Operations: Ability to edit and delete records directly from the web interface.

    - Reporting: Export capabilities to PDF and PNG for data snapshots.

📂 Project Structure
    The directory is organized as follows:

    final_project/
    ├── Scraper_data/
    │   ├── data/
    │   │   ├── air_quality.json          # Scraped real-time data
    │   │   └── history_air_quality.json  # Simulated historical data
    │   ├── scraper.py                    # Main scraping logic
    │   ├── generate_history.py           # Logic for historical simulation
    │   └── smooth_clean_api.py           # Data cleaning & smoothing class
    ├── src/
    │   ├── script.js                     # Frontend logic (Charts, Maps, API calls)
    │   └── style.css                     # Custom styling & animations
    ├── templates/
    │   └── index.html                    # Main dashboard frontend
    ├── .env                              # Environment variables (Host/Port)
    ├── myproject.py                      # Flask Server (Backend API)
    └── requirements.txt                  # Python dependencies

🛠️ Tech Stack
    - Backend: Python, Flask

    - Frontend: HTML5, Tailwind CSS, JavaScript (ES6)

    - Data Science: Pandas, Numpy

    - Libraries: Chart.js (Charts), Leaflet.js (Maps), html2canvas/jsPDF (Exports)

    -Data Source: WAQI API

🚀 Getting Started
1. Prerequisites
    - Python 3.x
    - A WAQI API Token (already configured in scraper.py)

2. Installation
    - Clone this repository to your local machine.

    - Install the required dependencies: pip install -r requirements.txt

3. Running the Application

    1. Scrape Data: The data is usually updated via the dashboard, but you can run the scraper manually:

        python Scraper_data/scraper.py

    2. Start the Flask Server:

        python myproject.py

    3. Access the Portal: Open your browser and navigate to: http://127.0.0.1:8000

🔌 API Endpoints
    The Flask server provides the following endpoints:

        - GET /: Renders the Home Page.

        - GET /api/current: Returns the current air quality dataset for all cities.

        - GET /api/history: Returns the historical air quality dataset.

        - POST /api/scrape: Triggers the scraper.py script to refresh data.

        - PUT /api/update/<id>: Updates a specific data record.

        - DELETE /api/delete/<id>: Removes a record from the local JSON storage.

📝 Author
    Nguyen Thanh Son Project for PY4E03 Course

