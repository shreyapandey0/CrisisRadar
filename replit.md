# CrisisRadar - India Crisis Detection System

## Overview

CrisisRadar is a comprehensive real-time crisis detection and monitoring system specifically designed for India. The system integrates multiple news APIs, government RSS feeds, machine learning classification, and multilingual capabilities to provide crisis detection, severity assessment, and emergency alerts across the Indian subcontinent.

## System Architecture

### Frontend Architecture
- **Streamlit Web Application**: Interactive dashboard with real-time crisis visualization
- **Folium Maps**: India-focused interactive mapping with state boundaries and crisis markers
- **Plotly Visualizations**: Advanced analytics and trend charts for crisis data
- **Multilingual UI**: Support for 14+ Indian languages including Hindi, Bengali, Tamil, Telugu

### Backend Architecture
- **Data Collection Layer**: Multi-source news aggregation from APIs and RSS feeds
- **ML Classification Engine**: Crisis type detection and severity assessment using scikit-learn
- **Language Processing**: Real-time translation and regional language support
- **Alert System**: SMS notifications via Twilio integration
- **Database Layer**: SQLite for data persistence and historical analysis

### Data Storage Solutions
- **SQLite Database**: Local file-based storage for crisis data, weather alerts, and user registrations
- **File-based Models**: Pickle serialization for trained ML models
- **Configuration**: Environment variables for API keys and sensitive data

## Key Components

### Data Collector (`data_collector.py`)
- Integrates NewsAPI, MediaStack, and NewsData.io for news aggregation
- Monitors government RSS feeds (IMD, NDMA, PIB)
- Collects weather data via Weatherstack API
- Filters and processes India-specific content
- Extracts full article content using trafilatura

### ML Classifier (`ml_classifier.py`)
- **Crisis Type Detection**: 8 categories (flood, earthquake, cyclone, fire, drought, landslide, storm, accident)
- **Severity Assessment**: 3 levels (low, medium, high)
- **Feature Engineering**: TF-IDF vectorization with keyword-based classification
- **Model Architecture**: Naive Bayes classifiers with confidence scoring
- **Training Data**: Synthetic and keyword-based training sets

### SMS Alerter (`sms_alerts.py`)
- Twilio integration for emergency notifications
- Location-based alert targeting with radius calculations
- Multilingual SMS templates (English, Hindi, Bengali, Tamil)
- User registration and preference management
- Duplicate alert prevention with cooldown periods

### Language Processor (`language_processor.py`)
- Google Translate API integration for real-time translation
- Crisis term dictionaries in 14+ Indian languages
- Language detection and text processing
- Regional crisis terminology mapping

### Database Management (`database.py`)
- SQLite schema for crisis data, weather alerts, and user management
- Historical data storage with trend analysis capabilities
- Data aggregation and filtering functions
- Performance optimization with indexing

### India Data (`india_data.py`)
- Comprehensive state and union territory information
- Major cities coordinates and demographics
- Emergency resource locations (hospitals, police, fire stations)
- Common disaster patterns by region

## Data Flow

1. **Data Collection**: Continuous monitoring of news APIs, RSS feeds, and weather services
2. **Content Processing**: Text extraction, cleaning, and India-specific filtering
3. **ML Classification**: Crisis type detection and severity assessment with confidence scoring
4. **Location Extraction**: Geographic entity recognition for Indian cities and states
5. **Database Storage**: Persistent storage of classified crisis events
6. **Alert Generation**: SMS notifications for registered users within affected areas
7. **Visualization**: Real-time dashboard updates with interactive maps and analytics

## External Dependencies

### News APIs
- **NewsAPI**: General news aggregation with India filtering
- **MediaStack**: Regional news sources with location-based filtering
- **NewsData.io**: Real-time news with crisis keyword monitoring

### Government Sources
- **IMD (India Meteorological Department)**: Weather warnings and forecasts
- **NDMA (National Disaster Management Authority)**: Official disaster alerts
- **PIB (Press Information Bureau)**: Government crisis communications

### Third-party Services
- **Twilio**: SMS notification delivery system
- **Google Translate**: Multilingual content processing
- **Weatherstack**: Weather data and extreme weather detection

### Python Libraries
- **Streamlit**: Web application framework
- **Folium**: Interactive mapping capabilities
- **Plotly**: Data visualization and analytics
- **scikit-learn**: Machine learning classification
- **Pandas/NumPy**: Data processing and analysis
- **SQLite3**: Database management

## Deployment Strategy

### Replit Configuration
- **Runtime**: Python 3.11 with Nix package management
- **Deployment Target**: Autoscale for dynamic resource allocation
- **Port Configuration**: Streamlit server on port 5000
- **Environment**: Secure environment variable management for API keys

### Scalability Considerations
- **Data Collection**: Rate-limited API calls with error handling
- **ML Processing**: Lightweight models for real-time classification
- **Database**: SQLite suitable for moderate traffic, easily upgradeable to Postgres
- **Alert System**: Asynchronous SMS processing with queue management

### Security Features
- **API Key Management**: Environment variable isolation
- **Data Sanitization**: Input validation and text cleaning
- **Rate Limiting**: API call throttling to prevent abuse
- **User Privacy**: Minimal data collection with opt-in alerts

## Changelog

```
Changelog:
- June 19, 2025. Initial setup
```

## User Preferences

```
Preferred communication style: Simple, everyday language.
```