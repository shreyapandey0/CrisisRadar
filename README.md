# CrisisRadar — Real-Time Local Crisis Detection & Resource Mapping

## Project Overview

CrisisRadar is an advanced real-time crisis detection and resource mapping system designed to monitor and respond to local disasters across India and select neighboring countries. It integrates multiple news and weather APIs, uses machine learning and natural language processing (NLP) for crisis classification, supports multiple Indian languages, and provides an interactive Streamlit dashboard for visualization and alerts.

## Features

- Real-time detection of local crises such as floods, earthquakes, cyclones, fires, droughts, landslides, and accidents.
- Aggregates data from multiple sources: MediaStack, NewsAPI, NewsData.io, Weatherstack, and government RSS feeds.
- Multilingual support with planned NLP classification in English, Hindi, Bengali, Tamil, and more.
- Interactive and attractive Streamlit dashboard with:
  - Live crisis map with severity-based markers and weather alerts.
  - Emergency resource layers including hospitals, police stations, and shelters.
  - Advanced analytics charts for crisis type, severity, and location distribution.
  - Live crisis intelligence feed with detailed alerts.
  - Emergency resources and preparedness guides.
- SMS alert registration and notification system via Twilio.
- Backend logging and error handling with no frontend error/success messages.

## Project Structure

- `crisis_radar_production.py`: Main Streamlit application with UI, map visualization, data collection, and alert registration.
- `data_collector.py`: Handles API data fetching and aggregation.
- `ml_classifier.py`: Contains machine learning and NLP models for crisis classification.
- `language_processor.py`: Language translation and processing utilities.
- `sms_alerts.py`: SMS alert sending via Twilio.
- `database.py`: SQLite database management and schema.
- `india_data.py`: Coordinates and location data for Indian cities and states.
- `utils.py`: Utility functions used across the project.
- `.env`: Environment variables including API keys and Twilio credentials.
- `crisis_radar_production.db`: SQLite database file storing crisis and weather data.

## Algorithm & Workflow

1. **Data Collection**: Periodically fetches news and weather data from multiple APIs and RSS feeds.
2. **Crisis Detection**: Uses keyword matching and ML/NLP classification to identify crisis-related events.
3. **Location Extraction**: Extracts and geocodes locations mentioned in news articles.
4. **Data Storage**: Stores crisis events, weather alerts, and user registrations in SQLite database.
5. **Visualization**: Displays live crisis data on an interactive map with severity-based markers and emergency resource layers.
6. **Analytics**: Provides charts summarizing crisis types, severity, and affected locations.
7. **Alerts**: Allows users to register for SMS alerts based on location and language preferences.
8. **Multilingual Support**: Plans to translate and classify news in multiple Indian languages for inclusiveness.

## Tech Stack

- Python 3.13
- Streamlit for frontend dashboard
- Plotly for interactive map and charts
- SQLite for local data storage
- Requests and Feedparser for API and RSS data fetching
- Twilio API for SMS alerts
- dotenv for environment variable management

## Setup & Running Locally

### Prerequisites

- Python 3.13 installed
- API keys for MediaStack, NewsAPI, NewsData.io, Weatherstack
- Twilio account with SID, Auth Token, and phone number

### Installation Steps

1. Clone the repository:

   ```
   git clone <repository_url>
   cd CrisisIntelMapper
   ```

2. Create and activate a virtual environment:

   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install required packages:

   ```
   pip install -r requirements.txt
   ```

4. Create a `.env` file in the project root with your API keys and Twilio credentials:

   ```
   NEWSAPI_KEY=your_newsapi_key
   MEDIASTACK_KEY=your_mediastack_key
   NEWSDATA_KEY=your_newsdata_key
   WEATHERSTACK_KEY=your_weatherstack_key
   TWILIO_ACCOUNT_SID=your_twilio_sid
   TWILIO_AUTH_TOKEN=your_twilio_auth_token
   TWILIO_PHONE_NUMBER=your_twilio_phone_number
   ```

5. Run the Streamlit app:

   ```
   streamlit run crisis_radar_production.py
   ```

6. Open the URL shown in the terminal (usually http://localhost:8501) in your browser.

### Usage

- Use the sidebar to test API connections, collect live data, or load stored data.
- Apply filters for crisis types, severity, and confidence threshold.
- Register for SMS alerts with your phone number and location.
- Explore the live crisis map, analytics, intelligence feed, and emergency resources tabs.

## Notes

- The system currently supports India and plans to extend to neighboring countries.
- The map includes major cities, crisis events by severity, weather alerts, and emergency resources.
- All error and success messages are logged in the backend; the frontend remains clean.
- The project uses free-tier API plans; rate limits may apply.

## Future Enhancements

- Full multilingual NLP classification and translation integration.
- More detailed emergency resource data with live updates.
- User authentication and personalized alert settings.
- Mobile app integration for wider accessibility.

---

Made with ❤️ for India's safety and resilience.
