import streamlit as st
import plotly.graph_objects as go
import requests
import json
import sqlite3
import logging
import os
import time
import feedparser
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging for backend only
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Suppress warnings
import warnings
warnings.filterwarnings('ignore')

# Page configuration
st.set_page_config(
    page_title="CrisisRadar - India Crisis Detection System",
    page_icon="🚨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for attractive UI
def load_custom_css():
    st.markdown("""
    <style>
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 15px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 8px 32px rgba(0,0,0,0.1);
    }
    .metric-container {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.08);
        border-left: 5px solid #FF6B6B;
        margin: 1rem 0;
        text-align: center;
    }
    .crisis-card {
        background: linear-gradient(135deg, #fff5f5 0%, #fed7d7 100%);
        border: none;
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 4px 15px rgba(255,107,107,0.1);
    }
    .emergency-card {
        background: linear-gradient(135deg, #f0fff4 0%, #c6f6d5 100%);
        border: none;
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 4px 15px rgba(72,187,120,0.1);
    }
    .status-online {
        color: #48BB78;
        font-weight: bold;
    }
    .status-offline {
        color: #F56565;
        font-weight: bold;
    }
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.5rem 1rem;
        font-weight: 600;
        width: 100%;
    }
    .stButton > button:hover {
        background: linear-gradient(135deg, #5a67d8 0%, #6b46c1 100%);
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.2);
    }
    .metric-value {
        font-size: 2.5rem;
        font-weight: bold;
        margin: 0.5rem 0;
    }
    .metric-label {
        font-size: 1rem;
        color: #666;
        margin-bottom: 0.5rem;
    }
    </style>
    """, unsafe_allow_html=True)

# Indian coordinates database
INDIAN_COORDINATES = {
    'mumbai': (19.0760, 72.8777), 'delhi': (28.6139, 77.2090), 
    'bangalore': (12.9716, 77.5946), 'hyderabad': (17.3850, 78.4867),
    'ahmedabad': (23.0225, 72.5714), 'chennai': (13.0827, 80.2707),
    'kolkata': (22.5726, 88.3639), 'pune': (18.5204, 73.8567),
    'jaipur': (26.9124, 75.7873), 'lucknow': (26.8467, 80.9462),
    'kanpur': (26.4499, 80.3319), 'nagpur': (21.1458, 79.0882),
    'indore': (22.7196, 75.8577), 'bhopal': (23.2599, 77.4126),
    'visakhapatnam': (17.6868, 83.2185), 'patna': (25.5941, 85.1376),
    'vadodara': (22.3072, 73.1812), 'ludhiana': (30.9010, 75.8573),
    'agra': (27.1767, 78.0081), 'nashik': (19.9975, 73.7898),
    'srinagar': (34.0837, 74.7973), 'guwahati': (26.1445, 91.7362),
    'chandigarh': (30.7333, 76.7794), 'thiruvananthapuram': (8.5241, 76.9366),
    'bhubaneswar': (20.2961, 85.8245), 'mysore': (12.2958, 76.6394),
    'goa': (15.2993, 74.1240), 'coimbatore': (11.0168, 76.9558),
    'madurai': (9.9252, 78.1198), 'varanasi': (25.3176, 82.9739),
    'allahabad': (25.4358, 81.8463), 'jodhpur': (26.2389, 73.0243),
    'kochi': (9.9312, 76.2673), 'vijayawada': (16.5062, 80.6480)
}

# Indian states data
INDIAN_STATES = {
    'Andhra Pradesh': (15.9129, 79.7400), 'Arunachal Pradesh': (28.2180, 94.7278),
    'Assam': (26.2006, 92.9376), 'Bihar': (25.0961, 85.3131),
    'Chhattisgarh': (21.2787, 81.8661), 'Goa': (15.2993, 74.1240),
    'Gujarat': (22.2587, 71.1924), 'Haryana': (29.0588, 76.0856),
    'Himachal Pradesh': (31.1048, 77.1734), 'Jharkhand': (23.6102, 85.2799),
    'Karnataka': (15.3173, 75.7139), 'Kerala': (10.8505, 76.2711),
    'Madhya Pradesh': (22.9734, 78.6569), 'Maharashtra': (19.7515, 75.7139),
    'Manipur': (24.6637, 93.9063), 'Meghalaya': (25.4670, 91.3662),
    'Mizoram': (23.1645, 92.9376), 'Nagaland': (26.1584, 94.5624),
    'Odisha': (20.9517, 85.0985), 'Punjab': (31.1471, 75.3412),
    'Rajasthan': (27.0238, 74.2179), 'Sikkim': (27.5330, 88.5122),
    'Tamil Nadu': (11.1271, 78.6569), 'Telangana': (18.1124, 79.0193),
    'Tripura': (23.9408, 91.9882), 'Uttarakhand': (30.0668, 79.0193),
    'Uttar Pradesh': (26.8467, 80.9462), 'West Bengal': (22.9868, 87.8550),
    'Delhi': (28.6139, 77.2090)
}

class CrisisRadarSystem:
    def __init__(self):
        self.newsapi_key = os.getenv("NEWSAPI_KEY")
        self.mediastack_key = os.getenv("MEDIASTACK_KEY")
        self.newsdata_key = os.getenv("NEWSDATA_KEY")
        self.weatherstack_key = os.getenv("WEATHERSTACK_KEY")
        
        self.crisis_keywords = [
            'flood', 'flooding', 'inundation', 'waterlogging', 'deluge',
            'earthquake', 'quake', 'tremor', 'seismic', 'magnitude',
            'cyclone', 'hurricane', 'typhoon', 'storm', 'tempest',
            'fire', 'wildfire', 'blaze', 'burning', 'arson',
            'drought', 'water shortage', 'dry spell', 'arid',
            'landslide', 'mudslide', 'rockfall', 'slope failure',
            'accident', 'crash', 'collision', 'explosion', 'collapse',
            'disaster', 'emergency', 'calamity', 'catastrophe',
            'evacuation', 'rescue', 'relief', 'alert', 'warning'
        ]
        
        # Enhanced Indian location terms
        self.indian_terms = [
            'india', 'indian', 'bharath', 'bharat', 'hindustan'
        ] + list(INDIAN_COORDINATES.keys()) + [s.lower() for s in INDIAN_STATES.keys()]
        
        # RSS feeds for government alerts
        self.rss_feeds = {
            'IMD_Weather': 'https://mausam.imd.gov.in/imd_latest/contents/all_warning.xml',
            'Times_of_India': 'https://timesofindia.indiatimes.com/rssfeedstopstories.cms',
            'Hindustan_Times': 'https://www.hindustantimes.com/feeds/rss/india-news/rssfeed.xml',
            'Indian_Express': 'https://indianexpress.com/section/india/feed/',
            'NDTV': 'https://feeds.feedburner.com/ndtvnews-india-news'
        }
        
        self.init_database()
    
    def init_database(self):
        """Initialize SQLite database with proper schema"""
        try:
            conn = sqlite3.connect('crisis_radar_production.db')
            cursor = conn.cursor()
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS crisis_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    description TEXT,
                    crisis_type TEXT,
                    severity TEXT,
                    location TEXT,
                    latitude REAL,
                    longitude REAL,
                    source TEXT,
                    confidence REAL,
                    url TEXT,
                    detected_keywords TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS weather_alerts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    city TEXT,
                    temperature REAL,
                    description TEXT,
                    wind_speed REAL,
                    severity TEXT,
                    latitude REAL,
                    longitude REAL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS sms_users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    phone TEXT UNIQUE,
                    location TEXT,
                    radius INTEGER DEFAULT 50,
                    language TEXT DEFAULT 'English',
                    registered_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.commit()
            conn.close()
            logger.info("Database initialized successfully")
        except Exception as e:
            logger.error(f"Database initialization error: {e}")
    
    def test_api_connections(self):
        """Test all API connections and return detailed status"""
        status = {}
        
        # Test MediaStack (most reliable)
        if self.mediastack_key:
            try:
                response = requests.get(
                    f"http://api.mediastack.com/v1/news?access_key={self.mediastack_key}&countries=in&limit=1",
                    timeout=10
                )
                if response.status_code == 200:
                    data = response.json()
                    if 'data' in data and len(data['data']) > 0:
                        status['MediaStack'] = f"Connected - {len(data['data'])} articles available"
                    else:
                        status['MediaStack'] = "Connected but no data"
                else:
                    status['MediaStack'] = f"Error {response.status_code}"
                logger.info(f"MediaStack Status: {status['MediaStack']}")
            except Exception as e:
                status['MediaStack'] = f'Connection Failed: {str(e)}'
                logger.error(f"MediaStack Error: {e}")
        else:
            status['MediaStack'] = 'No API Key'
        
        # Test NewsData.io
        if self.newsdata_key:
            try:
                response = requests.get(
                    f"https://newsdata.io/api/1/news?apikey={self.newsdata_key}&country=in&size=1",
                    timeout=10
                )
                if response.status_code == 200:
                    data = response.json()
                    if 'results' in data:
                        status['NewsData.io'] = f"Connected - {len(data['results'])} articles"
                    else:
                        status['NewsData.io'] = "Connected but no results"
                else:
                    status['NewsData.io'] = f"Error {response.status_code}"
                logger.info(f"NewsData.io Status: {status['NewsData.io']}")
            except Exception as e:
                status['NewsData.io'] = f'Connection Failed: {str(e)}'
                logger.error(f"NewsData.io Error: {e}")
        else:
            status['NewsData.io'] = 'No API Key'
        
        # Test NewsAPI (might be rate limited)
        if self.newsapi_key:
            try:
                response = requests.get(
                    f"https://newsapi.org/v2/top-headlines?country=in&apiKey={self.newsapi_key}",
                    timeout=10
                )
                if response.status_code == 200:
                    data = response.json()
                    status['NewsAPI'] = f"Connected - {len(data.get('articles', []))} articles"
                elif response.status_code == 429:
                    status['NewsAPI'] = "Rate Limited (Free tier exhausted)"
                else:
                    status['NewsAPI'] = f"Error {response.status_code}"
                logger.info(f"NewsAPI Status: {status['NewsAPI']}")
            except Exception as e:
                status['NewsAPI'] = f'Connection Failed: {str(e)}'
                logger.error(f"NewsAPI Error: {e}")
        else:
            status['NewsAPI'] = 'No API Key'
        
        # Test Weatherstack
        if self.weatherstack_key:
            try:
                response = requests.get(
                    f"http://api.weatherstack.com/current?access_key={self.weatherstack_key}&query=Delhi",
                    timeout=10
                )
                if response.status_code == 200:
                    data = response.json()
                    if 'current' in data:
                        status['Weatherstack'] = "Connected - Weather data available"
                    else:
                        status['Weatherstack'] = "Connected but no weather data"
                else:
                    status['Weatherstack'] = f"Error {response.status_code}"
                logger.info(f"Weatherstack Status: {status['Weatherstack']}")
            except Exception as e:
                status['Weatherstack'] = f'Connection Failed: {str(e)}'
                logger.error(f"Weatherstack Error: {e}")
        else:
            status['Weatherstack'] = 'No API Key'
        
        return status
    
    def collect_crisis_data(self):
        """Collect and analyze crisis data from multiple sources"""
        all_data = []
        
        # Collect from MediaStack (most reliable)
        all_data.extend(self._collect_mediastack_data())
        
        # Collect from NewsData.io
        all_data.extend(self._collect_newsdata_data())
        
        # Collect from RSS feeds
        all_data.extend(self._collect_rss_data())
        
        # Try NewsAPI if not rate limited
        try:
            all_data.extend(self._collect_newsapi_data())
        except:
            logger.info("NewsAPI skipped (likely rate limited)")
        
        # Filter and classify crisis data
        crisis_data = []
        for item in all_data:
            if self._is_crisis_related(item['title'] + ' ' + item['description']):
                crisis_info = self._classify_crisis(item['title'] + ' ' + item['description'])
                location = self._extract_location(item['title'] + ' ' + item['description'])
                coords = self._get_coordinates(location)
                
                crisis_item = {
                    'title': item['title'],
                    'description': item['description'],
                    'source': item['source'],
                    'url': item.get('url', ''),
                    'location': location or 'India',
                    'latitude': coords[0],
                    'longitude': coords[1],
                    'crisis_type': crisis_info['type'],
                    'severity': crisis_info['severity'],
                    'confidence': crisis_info['confidence'],
                    'detected_keywords': ', '.join(crisis_info['keywords'])
                }
                crisis_data.append(crisis_item)
        
        # Store in database
        self._store_crisis_data(crisis_data)
        logger.info(f"Collected and classified {len(crisis_data)} crisis events")
        return crisis_data
    
    def _collect_mediastack_data(self):
        """Collect data from MediaStack API"""
        data = []
        if not self.mediastack_key:
            return data
        
        try:
            # Get news with crisis keywords
            keywords = '|'.join(self.crisis_keywords[:10])  # Limit for URL length
            response = requests.get(
                f"http://api.mediastack.com/v1/news?access_key={self.mediastack_key}&countries=in&keywords={keywords}&limit=25",
                timeout=15
            )
            
            if response.status_code == 200:
                result = response.json()
                for article in result.get('data', []):
                    if article.get('title') and article.get('description'):
                        data.append({
                            'title': article['title'],
                            'description': article['description'] or article['title'],
                            'source': 'MediaStack',
                            'url': article.get('url', ''),
                            'published_at': article.get('published_at', '')
                        })
                
                logger.info(f"Collected {len(data)} articles from MediaStack")
        except Exception as e:
            logger.error(f"MediaStack collection error: {e}")
        
        return data
    
    def _collect_newsdata_data(self):
        """Collect data from NewsData.io API"""
        data = []
        if not self.newsdata_key:
            return data
        
        try:
            # Search for crisis-related news
            keywords = ' OR '.join(self.crisis_keywords[:8])
            response = requests.get(
                f"https://newsdata.io/api/1/news?apikey={self.newsdata_key}&country=in&q={keywords}&size=20",
                timeout=15
            )
            
            if response.status_code == 200:
                result = response.json()
                for article in result.get('results', []):
                    if article.get('title') and article.get('description'):
                        data.append({
                            'title': article['title'],
                            'description': article['description'] or article['title'],
                            'source': 'NewsData.io',
                            'url': article.get('link', ''),
                            'published_at': article.get('pubDate', '')
                        })
                
                logger.info(f"Collected {len(data)} articles from NewsData.io")
        except Exception as e:
            logger.error(f"NewsData.io collection error: {e}")
        
        return data
    
    def _collect_newsapi_data(self):
        """Collect data from NewsAPI (with rate limit handling)"""
        data = []
        if not self.newsapi_key:
            return data
        
        try:
            # Try a simple query first
            response = requests.get(
                f"https://newsapi.org/v2/everything?q=India disaster&sortBy=publishedAt&pageSize=15&apiKey={self.newsapi_key}",
                timeout=15
            )
            
            if response.status_code == 200:
                result = response.json()
                for article in result.get('articles', []):
                    if article.get('title') and article.get('description'):
                        data.append({
                            'title': article['title'],
                            'description': article['description'] or article['title'],
                            'source': f"NewsAPI - {article.get('source', {}).get('name', 'Unknown')}",
                            'url': article.get('url', ''),
                            'published_at': article.get('publishedAt', '')
                        })
                
                logger.info(f"Collected {len(data)} articles from NewsAPI")
            elif response.status_code == 429:
                logger.warning("NewsAPI rate limit exceeded")
        except Exception as e:
            logger.error(f"NewsAPI collection error: {e}")
        
        return data
    
    def _collect_rss_data(self):
        """Collect data from RSS feeds"""
        data = []
        
        for feed_name, feed_url in self.rss_feeds.items():
            try:
                feed = feedparser.parse(feed_url)
                for entry in feed.entries[:5]:  # Limit per feed
                    title = entry.get('title', '')
                    summary = entry.get('summary', entry.get('description', ''))
                    
                    if title and summary:
                        data.append({
                            'title': title,
                            'description': summary,
                            'source': f"RSS - {feed_name}",
                            'url': entry.get('link', ''),
                            'published_at': entry.get('published', '')
                        })
                
                time.sleep(0.5)  # Rate limiting
            except Exception as e:
                logger.error(f"RSS collection error for {feed_name}: {e}")
        
        logger.info(f"Collected {len(data)} items from RSS feeds")
        return data
    
    def _is_crisis_related(self, text):
        """Enhanced crisis detection with multiple criteria"""
        text_lower = text.lower()
        
        # Must be India-related
        india_related = any(term in text_lower for term in self.indian_terms)
        if not india_related:
            return False
        
        # Must contain crisis keywords
        crisis_related = any(keyword in text_lower for keyword in self.crisis_keywords)
        
        # Additional crisis indicators
        emergency_words = ['emergency', 'alert', 'warning', 'evacuate', 'rescue', 'damage', 'injured', 'killed', 'destroyed']
        emergency_related = any(word in text_lower for word in emergency_words)
        
        return crisis_related or emergency_related
    
    def _classify_crisis(self, text):
        """Enhanced crisis classification with keyword detection"""
        text_lower = text.lower()
        detected_keywords = []
        
        # Crisis type mapping with expanded keywords
        crisis_patterns = {
            'flood': ['flood', 'flooding', 'inundation', 'waterlogging', 'deluge', 'submerg', 'overflow'],
            'earthquake': ['earthquake', 'quake', 'tremor', 'seismic', 'magnitude', 'epicenter', 'aftershock'],
            'cyclone': ['cyclone', 'hurricane', 'typhoon', 'storm', 'tempest', 'wind speed', 'landfall'],
            'fire': ['fire', 'wildfire', 'blaze', 'burning', 'arson', 'flame', 'smoke'],
            'drought': ['drought', 'water shortage', 'dry spell', 'arid', 'scarcity', 'reservoir low'],
            'landslide': ['landslide', 'mudslide', 'rockfall', 'slope failure', 'hill collapse'],
            'storm': ['thunderstorm', 'lightning', 'hailstorm', 'dust storm', 'squall'],
            'accident': ['accident', 'crash', 'collision', 'derailment', 'explosion', 'collapse', 'building fall']
        }
        
        # Find matching crisis type
        crisis_type = 'accident'  # default
        max_matches = 0
        
        for c_type, keywords in crisis_patterns.items():
            matches = sum(1 for keyword in keywords if keyword in text_lower)
            if matches > max_matches:
                max_matches = matches
                crisis_type = c_type
                detected_keywords = [kw for kw in keywords if kw in text_lower]
        
        # Severity classification with enhanced keywords
        severity_indicators = {
            'high': ['severe', 'massive', 'devastating', 'major', 'critical', 'catastrophic', 'extreme', 'deadly', 'killed', 'died', 'death', 'hundreds', 'thousands'],
            'medium': ['moderate', 'significant', 'considerable', 'notable', 'substantial', 'injured', 'damaged', 'affected'],
            'low': ['minor', 'small', 'light', 'slight', 'minimal', 'reported', 'alert', 'warning']
        }
        
        severity = 'low'  # default
        for sev_level, keywords in severity_indicators.items():
            if any(keyword in text_lower for keyword in keywords):
                severity = sev_level
                detected_keywords.extend([kw for kw in keywords if kw in text_lower])
                break
        
        # Calculate confidence based on keyword matches and context
        total_indicators = len([kw for kw in self.crisis_keywords if kw in text_lower])
        emergency_indicators = len([word for word in ['emergency', 'alert', 'rescue', 'evacuate'] if word in text_lower])
        
        confidence = min(0.4 + (total_indicators * 0.15) + (emergency_indicators * 0.1), 1.0)
        
        return {
            'type': crisis_type,
            'severity': severity,
            'confidence': confidence,
            'keywords': list(set(detected_keywords))  # Remove duplicates
        }
    
    def _extract_location(self, text):
        """Enhanced location extraction"""
        text_lower = text.lower()
        
        # Check cities first (more specific)
        for city in INDIAN_COORDINATES.keys():
            if city in text_lower:
                return city.title()
        
        # Check for city variations
        city_variations = {
            'bombay': 'Mumbai', 'calcutta': 'Kolkata', 'madras': 'Chennai',
            'new delhi': 'Delhi', 'bengaluru': 'Bangalore'
        }
        
        for variation, proper_name in city_variations.items():
            if variation in text_lower:
                return proper_name
        
        # Check states
        for state in INDIAN_STATES.keys():
            if state.lower() in text_lower:
                return state
        
        return None
    
    def _get_coordinates(self, location):
        """Get coordinates for location"""
        if not location:
            return (20.5937, 78.9629)  # Center of India
        
        location_lower = location.lower()
        
        # Check cities
        if location_lower in INDIAN_COORDINATES:
            return INDIAN_COORDINATES[location_lower]
        
        # Check states
        if location in INDIAN_STATES:
            return INDIAN_STATES[location]
        
        return (20.5937, 78.9629)
    
    def collect_weather_data(self):
        """Collect weather alerts for major cities"""
        weather_data = []
        major_cities = ['Delhi', 'Mumbai', 'Bangalore', 'Chennai', 'Kolkata', 'Hyderabad', 'Pune', 'Jaipur']
        
        if not self.weatherstack_key:
            return weather_data
        
        for city in major_cities:
            try:
                response = requests.get(
                    f"http://api.weatherstack.com/current?access_key={self.weatherstack_key}&query={city}",
                    timeout=10
                )
                
                if response.status_code == 200:
                    data = response.json()
                    current = data.get('current', {})
                    location = data.get('location', {})
                    
                    temperature = current.get('temperature', 0)
                    weather_desc = current.get('weather_descriptions', [''])[0].lower()
                    wind_speed = current.get('wind_speed', 0)
                    
                    # Enhanced extreme weather detection
                    is_extreme = (
                        temperature > 45 or temperature < 2 or wind_speed > 50 or
                        any(extreme in weather_desc for extreme in [
                            'storm', 'heavy', 'severe', 'extreme', 'thunderstorm',
                            'cyclone', 'hurricane', 'tornado', 'hail'
                        ])
                    )
                    
                    if is_extreme:
                        severity = 'high' if (temperature > 47 or wind_speed > 80) else 'medium'
                        coords = INDIAN_COORDINATES.get(city.lower(), (20.5937, 78.9629))
                        
                        alert = {
                            'city': location.get('name', city),
                            'temperature': temperature,
                            'description': weather_desc,
                            'wind_speed': wind_speed,
                            'severity': severity,
                            'latitude': location.get('lat', coords[0]),
                            'longitude': location.get('lon', coords[1])
                        }
                        weather_data.append(alert)
                
                time.sleep(1)  # Rate limiting
            except Exception as e:
                logger.error(f"Weather API error for {city}: {e}")
        
        self._store_weather_data(weather_data)
        logger.info(f"Collected {len(weather_data)} weather alerts")
        return weather_data
    
    def _store_crisis_data(self, data):
        """Store crisis data in database"""
        if not data:
            return
        
        try:
            conn = sqlite3.connect('crisis_radar_production.db')
            cursor = conn.cursor()
            
            for item in data:
                cursor.execute('''
                    INSERT INTO crisis_events 
                    (title, description, crisis_type, severity, location, latitude, longitude, 
                     source, confidence, url, detected_keywords)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    item['title'], item['description'], item['crisis_type'], 
                    item['severity'], item['location'], item['latitude'], 
                    item['longitude'], item['source'], item['confidence'],
                    item['url'], item['detected_keywords']
                ))
            
            conn.commit()
            conn.close()
            logger.info(f"Stored {len(data)} crisis events in database")
        except Exception as e:
            logger.error(f"Database storage error: {e}")
    
    def _store_weather_data(self, data):
        """Store weather data in database"""
        if not data:
            return
        
        try:
            conn = sqlite3.connect('crisis_radar_production.db')
            cursor = conn.cursor()
            
            for item in data:
                cursor.execute('''
                    INSERT INTO weather_alerts 
                    (city, temperature, description, wind_speed, severity, latitude, longitude)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    item['city'], item['temperature'], item['description'], 
                    item['wind_speed'], item['severity'], item['latitude'], item['longitude']
                ))
            
            conn.commit()
            conn.close()
            logger.info(f"Stored {len(data)} weather alerts in database")
        except Exception as e:
            logger.error(f"Weather storage error: {e}")
    
    def get_recent_data(self, hours=24):
        """Get recent crisis and weather data from database"""
        try:
            conn = sqlite3.connect('crisis_radar_production.db')
            cursor = conn.cursor()
            
            # Get recent crisis data
            cursor.execute('''
                SELECT * FROM crisis_events 
                WHERE timestamp >= datetime('now', '-{} hours')
                ORDER BY timestamp DESC LIMIT 50
            '''.format(hours))
            
            crisis_rows = cursor.fetchall()
            crisis_data = []
            
            for row in crisis_rows:
                crisis_data.append({
                    'id': row[0], 'title': row[1], 'description': row[2],
                    'crisis_type': row[3], 'severity': row[4], 'location': row[5],
                    'latitude': row[6], 'longitude': row[7], 'source': row[8],
                    'confidence': row[9], 'url': row[10], 'detected_keywords': row[11],
                    'timestamp': row[12]
                })
            
            # Get recent weather data
            cursor.execute('''
                SELECT * FROM weather_alerts 
                WHERE timestamp >= datetime('now', '-{} hours')
                ORDER BY timestamp DESC LIMIT 20
            '''.format(hours))
            
            weather_rows = cursor.fetchall()
            weather_data = []
            
            for row in weather_rows:
                weather_data.append({
                    'id': row[0], 'city': row[1], 'temperature': row[2],
                    'description': row[3], 'wind_speed': row[4], 'severity': row[5],
                    'latitude': row[6], 'longitude': row[7], 'timestamp': row[8]
                })
            
            conn.close()
            return crisis_data, weather_data
            
        except Exception as e:
            logger.error(f"Data retrieval error: {e}")
            return [], []
    
    def register_sms_user(self, phone, location, radius=50, language='English'):
        """Register user for SMS alerts"""
        try:
            conn = sqlite3.connect('crisis_radar_production.db')
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO sms_users (phone, location, radius, language)
                VALUES (?, ?, ?, ?)
            ''', (phone, location, radius, language))
            
            conn.commit()
            conn.close()
            logger.info(f"User registered: {phone} for {location}")
            return True
        except Exception as e:
            logger.error(f"Registration error: {e}")
            return False

def create_india_map(crisis_data, weather_data):
    """Create enhanced interactive map with detailed visualization"""
    fig = go.Figure()
    
    # Add major Indian cities as base layer
    major_cities = [
        {'name': 'Delhi', 'lat': 28.6139, 'lon': 77.2090},
        {'name': 'Mumbai', 'lat': 19.0760, 'lon': 72.8777},
        {'name': 'Bangalore', 'lat': 12.9716, 'lon': 77.5946},
        {'name': 'Chennai', 'lat': 13.0827, 'lon': 80.2707},
        {'name': 'Kolkata', 'lat': 22.5726, 'lon': 88.3639},
        {'name': 'Hyderabad', 'lat': 17.3850, 'lon': 78.4867}
    ]
    
    # Add city markers as reference points
    fig.add_trace(go.Scattermapbox(
        lat=[city['lat'] for city in major_cities],
        lon=[city['lon'] for city in major_cities],
        mode='markers+text',
        marker=dict(
            size=8,
            color='#34495E',
            opacity=0.6,
            symbol='circle'
        ),
        text=[city['name'] for city in major_cities],
        textposition='top center',
        textfont=dict(size=10, color='#2C3E50'),
        hovertemplate='<b>%{text}</b><br>Major City<extra></extra>',
        name='Major Cities',
        showlegend=True
    ))
    
    # Add crisis markers with enhanced styling and clustering
    crisis_by_severity = {'high': [], 'medium': [], 'low': []}
    
    if crisis_data:
        for item in crisis_data:
            severity = item.get('severity', 'low')
            crisis_by_severity[severity].append(item)
        
        # Add high severity crises (most prominent)
        if crisis_by_severity['high']:
            high_items = crisis_by_severity['high']
            fig.add_trace(go.Scattermapbox(
                lat=[item['latitude'] for item in high_items],
                lon=[item['longitude'] for item in high_items],
                mode='markers',
                marker=dict(
                    size=20,
                    color='#FF1744',
                    opacity=0.9,
                    symbol='circle',
                    line=dict(width=3, color='#FFFFFF')
                ),
                text=[f"<b>🚨 HIGH SEVERITY CRISIS</b><br>" +
                      f"<b>Type:</b> {item['crisis_type'].title()}<br>" +
                      f"<b>Location:</b> {item['location']}<br>" +
                      f"<b>Confidence:</b> {item['confidence']:.0%}<br>" +
                      f"<b>Source:</b> {item['source']}<br>" +
                      f"<b>Title:</b> {item['title'][:100]}...<br>" +
                      f"<b>Keywords:</b> {item.get('detected_keywords', 'N/A')}"
                      for item in high_items],
                hovertemplate='%{text}<extra></extra>',
                name='High Severity Crisis',
                showlegend=True
            ))
        
        # Add medium severity crises
        if crisis_by_severity['medium']:
            medium_items = crisis_by_severity['medium']
            fig.add_trace(go.Scattermapbox(
                lat=[item['latitude'] for item in medium_items],
                lon=[item['longitude'] for item in medium_items],
                mode='markers',
                marker=dict(
                    size=16,
                    color='#FF9800',
                    opacity=0.8,
                    symbol='circle',
                    line=dict(width=2, color='#FFFFFF')
                ),
                text=[f"<b>⚠️ MEDIUM SEVERITY CRISIS</b><br>" +
                      f"<b>Type:</b> {item['crisis_type'].title()}<br>" +
                      f"<b>Location:</b> {item['location']}<br>" +
                      f"<b>Confidence:</b> {item['confidence']:.0%}<br>" +
                      f"<b>Source:</b> {item['source']}<br>" +
                      f"<b>Title:</b> {item['title'][:100]}...<br>" +
                      f"<b>Keywords:</b> {item.get('detected_keywords', 'N/A')}"
                      for item in medium_items],
                hovertemplate='%{text}<extra></extra>',
                name='Medium Severity Crisis',
                showlegend=True
            ))
        
        # Add low severity crises
        if crisis_by_severity['low']:
            low_items = crisis_by_severity['low']
            fig.add_trace(go.Scattermapbox(
                lat=[item['latitude'] for item in low_items],
                lon=[item['longitude'] for item in low_items],
                mode='markers',
                marker=dict(
                    size=12,
                    color='#FFC107',
                    opacity=0.7,
                    symbol='circle',
                    line=dict(width=1, color='#FFFFFF')
                ),
                text=[f"<b>📋 LOW SEVERITY CRISIS</b><br>" +
                      f"<b>Type:</b> {item['crisis_type'].title()}<br>" +
                      f"<b>Location:</b> {item['location']}<br>" +
                      f"<b>Confidence:</b> {item['confidence']:.0%}<br>" +
                      f"<b>Source:</b> {item['source']}<br>" +
                      f"<b>Title:</b> {item['title'][:100]}...<br>" +
                      f"<b>Keywords:</b> {item.get('detected_keywords', 'N/A')}"
                      for item in low_items],
                hovertemplate='%{text}<extra></extra>',
                name='Low Severity Crisis',
                showlegend=True
            ))
    
    # Add weather alerts with enhanced details
    if weather_data:
        fig.add_trace(go.Scattermapbox(
            lat=[item['latitude'] for item in weather_data],
            lon=[item['longitude'] for item in weather_data],
            mode='markers',
            marker=dict(
                size=18,
                color='#2196F3',
                opacity=0.8,
                symbol='diamond',
                line=dict(width=2, color='#FFFFFF')
            ),
            text=[f"<b>🌩️ WEATHER ALERT</b><br>" +
                  f"<b>City:</b> {item['city']}<br>" +
                  f"<b>Temperature:</b> {item['temperature']}°C<br>" +
                  f"<b>Condition:</b> {item['description']}<br>" +
                  f"<b>Wind Speed:</b> {item['wind_speed']} km/h<br>" +
                  f"<b>Severity:</b> {item['severity'].title()}"
                  for item in weather_data],
            hovertemplate='%{text}<extra></extra>',
            name='Weather Alert',
            showlegend=True
        ))
    
    # Enhanced layout with better styling
    fig.update_layout(
        mapbox=dict(
            style="open-street-map",
            center=dict(lat=20.5937, lon=78.9629),
            zoom=4.8,
            bearing=0,
            pitch=0
        ),
        height=700,
        margin=dict(l=0, r=0, t=40, b=0),
        title=dict(
            text="Live Crisis Detection Map - India",
            x=0.5,
            y=0.97,
            xanchor='center',
            yanchor='top',
            font=dict(size=18, color='#2F3349')
        ),
        legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=0.01,
            bgcolor="rgba(255,255,255,0.9)",
            bordercolor="rgba(0,0,0,0.2)",
            borderwidth=1,
            font=dict(size=11)
        ),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )
    
    return fig

def create_analytics_charts(crisis_data):
    """Create comprehensive analytics charts without any external dependencies"""
    if not crisis_data:
        return None, None, None
    
    # Crisis type distribution
    type_counts = {}
    for item in crisis_data:
        crisis_type = item['crisis_type']
        type_counts[crisis_type] = type_counts.get(crisis_type, 0) + 1
    
    # Create pie chart using plotly.graph_objects only
    fig_pie = go.Figure(data=[go.Pie(
        labels=list(type_counts.keys()),
        values=list(type_counts.values()),
        hole=0.3,
        textinfo='label+percent',
        textposition='auto',
        marker=dict(
            colors=['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7', '#DDA0DD', '#98D8C8', '#F7DC6F'],
            line=dict(color='#FFFFFF', width=2)
        )
    )])
    fig_pie.update_layout(
        title={
            'text': "Crisis Types Distribution",
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 20, 'color': '#2F3349'}
        },
        height=450,
        showlegend=True,
        legend=dict(
            orientation="v",
            yanchor="middle",
            y=0.5,
            xanchor="left",
            x=1.05
        ),
        font=dict(size=12),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )
    
    # Severity distribution
    severity_counts = {}
    for item in crisis_data:
        severity = item['severity']
        severity_counts[severity] = severity_counts.get(severity, 0) + 1
    
    severity_order = ['high', 'medium', 'low']  # Ensure consistent ordering
    ordered_severities = []
    ordered_counts = []
    ordered_colors = []
    
    colors = {'high': '#FF1744', 'medium': '#FF9800', 'low': '#FFC107'}
    
    for severity in severity_order:
        if severity in severity_counts:
            ordered_severities.append(severity.upper())
            ordered_counts.append(severity_counts[severity])
            ordered_colors.append(colors[severity])
    
    fig_bar = go.Figure(data=[go.Bar(
        x=ordered_severities,
        y=ordered_counts,
        marker=dict(
            color=ordered_colors,
            line=dict(color='#FFFFFF', width=1)
        ),
        text=ordered_counts,
        textposition='auto',
        textfont=dict(size=14, color='white')
    )])
    fig_bar.update_layout(
        title={
            'text': "Crisis Severity Distribution",
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 20, 'color': '#2F3349'}
        },
        height=450,
        xaxis=dict(
            title="Severity Level",
            titlefont=dict(size=14),
            tickfont=dict(size=12)
        ),
        yaxis=dict(
            title="Number of Events",
            titlefont=dict(size=14),
            tickfont=dict(size=12)
        ),
        showlegend=False,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=60, r=60, t=80, b=60)
    )
    
    # Location analysis
    location_counts = {}
    for item in crisis_data:
        location = item['location']
        if location and location != 'India':
            location_counts[location] = location_counts.get(location, 0) + 1
    
    if location_counts and len(location_counts) > 0:
        # Top 10 locations
        sorted_locations = sorted(location_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        locations = [item[0] for item in sorted_locations]
        counts = [item[1] for item in sorted_locations]
        
        # Create color scale based on values
        max_count = max(counts) if counts else 1
        colors_scale = [f'rgba(255, 87, 51, {0.3 + 0.7 * (count/max_count)})' for count in counts]
        
        fig_location = go.Figure(data=[go.Bar(
            x=counts,
            y=locations,
            orientation='h',
            marker=dict(
                color=colors_scale,
                line=dict(color='#FF5733', width=1)
            ),
            text=[f'{count} events' for count in counts],
            textposition='auto',
            textfont=dict(size=11, color='white')
        )])
        fig_location.update_layout(
            title={
                'text': "Top Affected Locations",
                'x': 0.5,
                'xanchor': 'center',
                'font': {'size': 20, 'color': '#2F3349'}
            },
            height=450,
            xaxis=dict(
                title="Number of Events",
                titlefont=dict(size=14),
                tickfont=dict(size=12)
            ),
            yaxis=dict(
                title="Location",
                titlefont=dict(size=14),
                tickfont=dict(size=11)
            ),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            margin=dict(l=120, r=60, t=80, b=60)
        )
    else:
        fig_location = None
    
    return fig_pie, fig_bar, fig_location

def main():
    """Main application with enhanced functionality"""
    load_custom_css()
    
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>🚨 CrisisRadar</h1>
        <h3>Advanced Real-Time Crisis Detection & Emergency Response System for India</h3>
        <p>AI-Powered • Multi-Source Intelligence • 24/7 Monitoring • Real-Time Alerts</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Initialize system
    if 'crisis_system' not in st.session_state:
        with st.spinner("Initializing CrisisRadar System..."):
            st.session_state.crisis_system = CrisisRadarSystem()
            st.session_state.crisis_data = []
            st.session_state.weather_data = []
            st.session_state.last_update = None
    
    # Sidebar
    with st.sidebar:
        st.markdown("### 🎛️ Crisis Control Center")
        
        # API Status Check
        if st.button("🔍 Test API Connections"):
            with st.spinner("Testing all API connections..."):
                api_status = st.session_state.crisis_system.test_api_connections()
                
                st.markdown("#### 📡 API Connection Status")
                for api, status in api_status.items():
                    if 'Connected' in status:
                        st.markdown(f"✅ **{api}**: <span class='status-online'>{status}</span>", unsafe_allow_html=True)
                    elif 'Rate Limited' in status:
                        st.markdown(f"⚠️ **{api}**: <span style='color: orange;'>{status}</span>", unsafe_allow_html=True)
                    else:
                        st.markdown(f"❌ **{api}**: <span class='status-offline'>{status}</span>", unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Real-time Data Collection
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("📡 Collect Live Data"):
                with st.spinner("Collecting real-time crisis data..."):
                    try:
                        crisis_data = st.session_state.crisis_system.collect_crisis_data()
                        weather_data = st.session_state.crisis_system.collect_weather_data()
                        
                        st.session_state.crisis_data = crisis_data
                        st.session_state.weather_data = weather_data
                        st.session_state.last_update = datetime.now()
                        
                        st.success(f"✅ Found {len(crisis_data)} crisis events and {len(weather_data)} weather alerts")
                    except Exception as e:
                        st.error("❌ Data collection failed. Check API keys.")
                        logger.error(f"Data collection error: {e}")
        
        with col2:
            if st.button("📂 Load Stored Data"):
                crisis_data, weather_data = st.session_state.crisis_system.get_recent_data()
                st.session_state.crisis_data = crisis_data
                st.session_state.weather_data = weather_data
                st.info(f"📊 Loaded {len(crisis_data)} stored events")
        
        st.markdown("---")
        
        # Filters and Settings
        st.markdown("#### 🎯 Detection Filters")
        
        crisis_filter = st.multiselect(
            "Crisis Types",
            ["flood", "earthquake", "cyclone", "fire", "drought", "landslide", "storm", "accident"],
            default=["flood", "earthquake", "cyclone", "fire"]
        )
        
        severity_filter = st.multiselect(
            "Severity Levels",
            ["high", "medium", "low"],
            default=["high", "medium", "low"]
        )
        
        confidence_threshold = st.slider(
            "Confidence Threshold", 0.0, 1.0, 0.5, 0.1,
            help="Minimum confidence level for crisis detection"
        )
        
        # Language Selection
        language = st.selectbox(
            "🌐 Language",
            ["English", "हिंदी (Hindi)", "বাংলা (Bengali)", "தமிழ் (Tamil)", "తెలుగు (Telugu)", "मराठी (Marathi)"]
        )
        
        st.markdown("---")
        
        # SMS Alert Registration
        st.markdown("#### 📱 Emergency SMS Alerts")
        with st.expander("Register for Alerts"):
            phone = st.text_input("📞 Phone Number (+91XXXXXXXXXX)")
            location = st.selectbox("📍 Your Location", ["Select..."] + list(INDIAN_STATES.keys()) + list(INDIAN_COORDINATES.keys()))
            radius = st.slider("Alert Radius (km)", 10, 500, 50)
            
            if st.button("🔔 Register for SMS Alerts"):
                if phone and location != "Select...":
                    success = st.session_state.crisis_system.register_sms_user(phone, location, radius, language)
                    if success:
                        st.success("✅ Successfully registered!")
                    else:
                        st.error("❌ Registration failed")
                else:
                    st.error("Please provide phone number and location")
    
    # Main Dashboard Metrics
    col1, col2, col3, col4 = st.columns(4)
    
    total_crises = len(st.session_state.crisis_data)
    high_severity = len([c for c in st.session_state.crisis_data if c.get('severity') == 'high'])
    weather_alerts = len(st.session_state.weather_data)
    last_update = st.session_state.last_update.strftime("%H:%M:%S") if st.session_state.last_update else "Never"
    
    with col1:
        st.markdown(f"""
        <div class="metric-container">
            <div class="metric-label">🚨 Active Crises</div>
            <div class="metric-value" style="color: #FF6B6B;">{total_crises}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-container">
            <div class="metric-label">🔴 High Severity</div>
            <div class="metric-value" style="color: #FF1744;">{high_severity}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="metric-container">
            <div class="metric-label">🌩️ Weather Alerts</div>
            <div class="metric-value" style="color: #2196F3;">{weather_alerts}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="metric-container">
            <div class="metric-label">🕐 Last Update</div>
            <div class="metric-value" style="color: #4CAF50; font-size: 1.5rem;">{last_update}</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Main Content Tabs
    tab1, tab2, tab3, tab4 = st.tabs(["🗺️ Live Crisis Map", "📊 Advanced Analytics", "📰 Crisis Intelligence", "🏥 Emergency Resources"])
    
    with tab1:
        st.markdown("### 🗺️ Real-Time Crisis Map of India")
        
        # Apply filters
        filtered_crisis = st.session_state.crisis_data
        if crisis_filter:
            filtered_crisis = [c for c in filtered_crisis if c.get('crisis_type') in crisis_filter]
        if severity_filter:
            filtered_crisis = [c for c in filtered_crisis if c.get('severity') in severity_filter]
        
        filtered_crisis = [c for c in filtered_crisis if c.get('confidence', 0) >= confidence_threshold]
        
        if filtered_crisis or st.session_state.weather_data:
            map_fig = create_india_map(filtered_crisis, st.session_state.weather_data)
            st.plotly_chart(map_fig, use_container_width=True)
            
            # Enhanced legend
            st.markdown("""
            #### 🎯 Map Legend & Information
            - 🔴 **Red Circles**: High Severity Crisis Events
            - 🟠 **Orange Circles**: Medium Severity Crisis Events
            - 🟡 **Yellow Circles**: Low Severity Crisis Events
            - 🔵 **Blue Circles**: Extreme Weather Alerts
            
            **Click on any marker for detailed information including source, confidence level, and detected keywords.**
            """)
            
            # Summary statistics
            if filtered_crisis:
                st.markdown(f"**Displaying {len(filtered_crisis)} crisis events** (filtered from {len(st.session_state.crisis_data)} total)")
        else:
            st.info("🔍 No crisis data matching current filters. Try adjusting filters or collecting new data.")
    
    with tab2:
        st.markdown("### 📊 Crisis Analytics Dashboard")
        
        if st.session_state.crisis_data:
            # Filter data for analytics
            filtered_data = [c for c in st.session_state.crisis_data if c.get('confidence', 0) >= confidence_threshold]
            
            if filtered_data:
                col1, col2 = st.columns(2)
                
                pie_fig, bar_fig, location_fig = create_analytics_charts(filtered_data)
                
                with col1:
                    if pie_fig:
                        st.plotly_chart(pie_fig, use_container_width=True)
                    if location_fig:
                        st.plotly_chart(location_fig, use_container_width=True)
                
                with col2:
                    if bar_fig:
                        st.plotly_chart(bar_fig, use_container_width=True)
                    
                    # Enhanced statistics
                    st.markdown("#### 📈 Detailed Statistics")
                    
                    unique_locations = len(set(c['location'] for c in filtered_data if c['location'] and c['location'] != 'India'))
                    avg_confidence = sum(c['confidence'] for c in filtered_data) / len(filtered_data)
                    most_common_type = max(set(c['crisis_type'] for c in filtered_data), 
                                         key=lambda x: sum(1 for c in filtered_data if c['crisis_type'] == x))
                    
                    st.metric("Total Verified Reports", len(filtered_data))
                    st.metric("Unique Affected Locations", unique_locations)
                    st.metric("Average Detection Confidence", f"{avg_confidence:.0%}")
                    st.metric("Most Common Crisis Type", most_common_type.title())
                    
                    # Source breakdown
                    sources = {}
                    for item in filtered_data:
                        source = item['source']
                        sources[source] = sources.get(source, 0) + 1
                    
                    st.markdown("**Data Sources:**")
                    for source, count in sources.items():
                        st.write(f"• {source}: {count} reports")
            else:
                st.warning("No data meets the current confidence threshold. Try lowering the threshold.")
        else:
            st.info("📊 No data available for analytics. Please collect data first.")
    
    with tab3:
        st.markdown("### 📰 Live Crisis Intelligence Feed")
        
        if st.session_state.crisis_data:
            # Filter and sort data
            display_data = [c for c in st.session_state.crisis_data if c.get('confidence', 0) >= confidence_threshold]
            display_data.sort(key=lambda x: x.get('confidence', 0), reverse=True)
            
            for i, alert in enumerate(display_data[:15]):  # Show top 15
                severity_colors = {"high": "#FF1744", "medium": "#FF9800", "low": "#FFC107"}
                color = severity_colors.get(alert.get('severity', 'low'), '#999999')
                
                st.markdown(f"""
                <div class="crisis-card" style="border-left: 5px solid {color};">
                    <h4>🚨 {alert.get('title', 'Crisis Alert')}</h4>
                    <div style="display: flex; justify-content: space-between; margin-bottom: 10px;">
                        <span><strong>Type:</strong> {alert.get('crisis_type', 'Unknown').title()}</span>
                        <span><strong>Severity:</strong> {alert.get('severity', 'Unknown').title()}</span>
                        <span><strong>Confidence:</strong> {alert.get('confidence', 0):.0%}</span>
                    </div>
                    <p><strong>Location:</strong> {alert.get('location', 'Unknown')} | 
                       <strong>Source:</strong> {alert.get('source', 'Unknown')}</p>
                    <p>{alert.get('description', 'No description available')}</p>
                    <p style="font-size: 0.9em; color: #666;">
                        <strong>Detected Keywords:</strong> {alert.get('detected_keywords', 'N/A')}
                    </p>
                    {f'<p><a href="{alert.get("url", "#")}" target="_blank">📰 Read Full Article</a></p>' if alert.get('url') else ''}
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("📰 No crisis intelligence available. Click 'Collect Live Data' to start monitoring.")
    
    with tab4:
        st.markdown("### 🏥 Emergency Resources & Response")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("""
            <div class="emergency-card">
                <h4>🚨 National Emergency Numbers</h4>
                <p><strong>Police:</strong> 100</p>
                <p><strong>Fire Brigade:</strong> 101</p>
                <p><strong>Ambulance:</strong> 108</p>
                <p><strong>Disaster Management:</strong> 1078</p>
                <p><strong>Tourist Helpline:</strong> 1363</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div class="emergency-card">
                <h4>📞 Specialized Helplines</h4>
                <p><strong>Women Helpline:</strong> 1091</p>
                <p><strong>Child Helpline:</strong> 1098</p>
                <p><strong>Senior Citizen:</strong> 14567</p>
                <p><strong>Mental Health:</strong> 9152987821</p>
                <p><strong>COVID Helpline:</strong> 1075</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown("""
            <div class="emergency-card">
                <h4>🚛 Transport Emergency</h4>
                <p><strong>Railway Accident:</strong> 1072</p>
                <p><strong>Road Accident:</strong> 1073</p>
                <p><strong>Highway Emergency:</strong> 1033</p>
                <p><strong>Aviation Emergency:</strong> 1678</p>
                <p><strong>Coast Guard:</strong> 1554</p>
            </div>
            """, unsafe_allow_html=True)
        
        # Emergency preparedness
        st.markdown("#### 🎯 Crisis Preparedness Guide")
        
        prep_col1, prep_col2 = st.columns(2)
        
        with prep_col1:
            st.markdown("""
            **📋 Emergency Kit Essentials:**
            • 3 days of water (1 gallon per person per day)
            • Non-perishable food for 3 days
            • First aid kit and medications
            • Flashlight and extra batteries
            • Battery-powered or hand crank radio
            • Important family documents (copies)
            • Cash and credit cards
            • Emergency contact information
            """)
        
        with prep_col2:
            st.markdown("""
            **📱 Digital Preparedness:**
            • Download offline maps of your area
            • Keep emergency contact list in phone
            • Install weather and emergency alert apps
            • Backup important data to cloud
            • Keep portable chargers ready
            • Know your evacuation routes
            • Register for local emergency alerts
            • Follow official social media accounts
            """)
    
    # Footer with system status
    st.markdown("---")
    st.markdown(f"""
    <div style="text-align: center; color: #666; padding: 1rem;">
        <p><strong>CrisisRadar v2.0 - Production</strong> | Real-Time Crisis Intelligence for India</p>
        <p>System Status: <span style="color: #4CAF50;">🟢 ONLINE</span> | 
           Last Data Collection: {last_update} | 
           Total Events Monitored: {len(st.session_state.crisis_data)}</p>
        <p>Built with AI • Powered by Multiple APIs • Made for India's Safety</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()