# CrisisRadar - India Crisis Detection System 🚨

A comprehensive real-time crisis detection and monitoring system specifically designed for India, integrating multiple news APIs, government RSS feeds, machine learning classification, and multilingual SMS alert capabilities.

## 🌟 Features

### 🔍 Real-Time Crisis Detection
- **Multi-Source Data Integration**: NewsAPI, MediaStack, NewsData.io APIs
- **Government RSS Feeds**: IMD, NDMA, PIB, and state disaster management authorities
- **Major News Sources**: NDTV, Times of India, Hindustan Times, Indian Express
- **Weather Monitoring**: Weatherstack API for extreme weather detection

### 🤖 Advanced ML Classification
- **Crisis Type Detection**: Floods, earthquakes, cyclones, fires, droughts, landslides, accidents
- **Severity Assessment**: High, medium, low severity classification
- **Location Extraction**: Automatic Indian city/state identification from text
- **Confidence Scoring**: ML confidence levels for each classification

### 🗺️ Interactive Visualization
- **India-Focused Map**: Folium-based interactive map centered on India
- **Crisis Markers**: Color-coded severity indicators (red=high, orange=medium, yellow=low)
- **State Boundaries**: Visual state/UT boundaries with emergency resource locations
- **Real-Time Updates**: Auto-refresh capabilities every 30 seconds

### 📱 SMS Alert System
- **Twilio Integration**: Real-time SMS alerts for registered users
- **Location-Based Alerts**: Radius-based alert targeting
- **Multilingual Support**: Hindi, Bengali, Tamil, Telugu, Marathi, Gujarati, and more
- **Smart Filtering**: Prevents spam with duplicate alert detection

### 🌐 Multilingual Capabilities
- **Language Detection**: Automatic detection of regional language content
- **Real-Time Translation**: Google Translate API integration
- **Regional Crisis Terms**: Built-in dictionaries for crisis terms in Indian languages
- **Multilingual UI**: Dashboard and alerts in preferred Indian languages

### 📊 Advanced Analytics
- **Crisis Trends**: Historical data analysis and visualization
- **Geographic Distribution**: State-wise and city-wise crisis mapping
- **Severity Analysis**: Trend analysis by crisis severity levels
- **Performance Metrics**: API usage statistics and system health monitoring

### 🏥 Emergency Resources
- **Hospital Locator**: Major hospitals across Indian cities
- **Police Stations**: Law enforcement contact information
- **Fire Stations**: Fire department locations and contacts
- **Relief Shelters**: NGO and government shelter information

## 🏗️ System Architecture

