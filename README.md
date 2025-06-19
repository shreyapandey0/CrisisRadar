# CrisisRadar - India Crisis Detection System

## Overview

CrisisRadar is a comprehensive real-time crisis detection and monitoring system specifically designed for India. The system integrates multiple news APIs, government RSS feeds, machine learning classification, and multilingual capabilities to provide crisis detection, severity assessment, and emergency alerts across the Indian subcontinent.

## Features

### Core Functionality
- **Real-time Crisis Detection**: Monitors multiple news APIs and RSS feeds for crisis events
- **AI-Powered Classification**: Detects 8 types of crises (flood, earthquake, cyclone, fire, drought, landslide, storm, accident)
- **Severity Assessment**: Classifies events as high, medium, or low severity with confidence scoring
- **Interactive Map**: Live crisis visualization on India map with detailed markers
- **Advanced Analytics**: Comprehensive charts showing crisis distribution and trends
- **SMS Alerts**: Twilio-powered emergency notifications for registered users
- **Multilingual Support**: 6+ Indian languages including Hindi, Bengali, Tamil, Telugu

### Data Sources
- **News APIs**: MediaStack, NewsData.io, NewsAPI
- **Government RSS**: IMD (Weather), NDMA (Disasters), PIB (Government)
- **Weather Monitoring**: Weatherstack API for extreme weather detection
- **Regional Sources**: Major Indian news outlets and government feeds

### Technical Architecture
- **Frontend**: Streamlit web application with enhanced UI
- **Backend**: Python-based data processing and ML classification
- **Database**: SQLite for data persistence and historical analysis
- **APIs**: RESTful integration with multiple external services
- **Alerts**: SMS notifications via Twilio integration

## Quick Start

### Prerequisites
- Python 3.11+
- API keys for external services (see Configuration section)

### Installation
```bash
# Clone repository
git clone <repository-url>
cd crisisradar

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your API keys
```

### Running the Application
```bash
streamlit run crisis_radar_production.py --server.port 5000
```

The application will be available at `http://localhost:5000`

## Configuration

### Required API Keys
Create a `.env` file with the following variables:

```env
# News APIs
NEWSAPI_KEY=your_newsapi_key_here
MEDIASTACK_KEY=your_mediastack_key_here
NEWSDATA_KEY=your_newsdata_key_here

# Weather API
WEATHERSTACK_KEY=your_weatherstack_key_here

# SMS Alerts (Twilio)
TWILIO_ACCOUNT_SID=your_twilio_account_sid
TWILIO_AUTH_TOKEN=your_twilio_auth_token
TWILIO_PHONE_NUMBER=your_twilio_phone_number
```

### API Key Setup
1. **NewsAPI**: Get free API key from [newsapi.org](https://newsapi.org)
2. **MediaStack**: Register at [mediastack.com](https://mediastack.com)
3. **NewsData.io**: Sign up at [newsdata.io](https://newsdata.io)
4. **Weatherstack**: Get API key from [weatherstack.com](https://weatherstack.com)
5. **Twilio**: Create account at [twilio.com](https://twilio.com) for SMS alerts

## Usage Guide

### Dashboard Navigation
1. **Live Crisis Map**: Interactive map showing real-time crisis events
2. **Analytics**: Charts and statistics about crisis distribution
3. **Crisis Intelligence**: Detailed feed of detected crisis events
4. **Emergency Resources**: Contact numbers and preparedness information

### Data Collection
- Click "Collect Live Data" to fetch real-time crisis information
- Use "Load Stored Data" to view historical events
- Apply filters to focus on specific crisis types or severity levels

### SMS Alerts
1. Navigate to SMS Alerts section in sidebar
2. Enter phone number in international format (+91XXXXXXXXXX)
3. Select your location and alert radius
4. Choose preferred language
5. Click "Register for SMS Alerts"

### Filters and Settings
- **Crisis Types**: Filter by specific disaster types
- **Severity Levels**: Focus on high, medium, or low severity events
- **Confidence Threshold**: Adjust minimum confidence for detection
- **Language**: Select interface language

## System Architecture

### Components
- **crisis_radar_production.py**: Main application file with integrated functionality
- **Database Schema**: SQLite tables for crisis events, weather alerts, and user registrations
- **API Integration**: Multi-source data collection with error handling
- **ML Classification**: Keyword-based crisis detection and severity assessment

### Data Flow
1. **Collection**: APIs and RSS feeds provide raw news data
2. **Processing**: Text analysis and India-specific filtering
3. **Classification**: ML models detect crisis type and severity
4. **Storage**: Events stored in SQLite database
5. **Visualization**: Real-time updates to map and analytics
6. **Alerts**: SMS notifications sent to relevant users

## API Status and Monitoring

The system provides real-time API status monitoring:
- **MediaStack**: Primary news source (most reliable)
- **NewsData.io**: Secondary news source
- **NewsAPI**: Rate-limited free tier
- **Weatherstack**: Weather data and alerts

Use "Test API Connections" to verify all services are operational.

## Crisis Types Detected

1. **Flood**: Flooding, waterlogging, inundation
2. **Earthquake**: Seismic activity, tremors
3. **Cyclone**: Hurricanes, typhoons, severe storms
4. **Fire**: Wildfires, building fires, industrial fires
5. **Drought**: Water shortages, dry conditions
6. **Landslide**: Mudslides, slope failures
7. **Storm**: Thunderstorms, hailstorms, dust storms
8. **Accident**: Transportation, industrial, building accidents

## Emergency Contacts

### National Emergency Numbers
- **Police**: 100
- **Fire Brigade**: 101
- **Ambulance**: 108
- **Disaster Management**: 1078
- **Tourist Helpline**: 1363

### Specialized Helplines
- **Women Helpline**: 1091
- **Child Helpline**: 1098
- **Senior Citizen**: 14567
- **Mental Health**: 9152987821

## Troubleshooting

### Common Issues
1. **No Data Appearing**: Check API keys in .env file
2. **Rate Limit Errors**: Wait for rate limit reset or upgrade API plan
3. **Map Not Loading**: Verify internet connection and refresh page
4. **SMS Alerts Not Working**: Verify Twilio credentials and phone number format

### API Rate Limits
- **NewsAPI**: 100 requests/day (free tier)
- **MediaStack**: 500 requests/month (free tier)
- **NewsData.io**: 200 requests/day (free tier)
- **Weatherstack**: 1000 requests/month (free tier)

### Support
For technical issues or feature requests, please check the logs in the application or contact the development team.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Indian Meteorological Department (IMD) for weather data
- National Disaster Management Authority (NDMA) for disaster alerts
- Press Information Bureau (PIB) for government communications
- All news organizations providing crisis information

---

**CrisisRadar v2.0 Production** - Real-Time Crisis Intelligence for India's Safety
Built with Python • Powered by AI • Made for India