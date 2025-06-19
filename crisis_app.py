import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import requests
import json
import sqlite3
import logging
import os
import time
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
    .sidebar .sidebar-content {
        background: linear-gradient(180deg, #667eea 0%, #764ba2 100%);
    }
    .stSelectbox > div > div {
        background-color: #f8f9fa;
        border-radius: 8px;
    }
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.5rem 1rem;
        font-weight: 600;
    }
    .stButton > button:hover {
        background: linear-gradient(135deg, #5a67d8 0%, #6b46c1 100%);
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
    'goa': (15.2993, 74.1240), 'coimbatore': (11.0168, 76.9558)
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

class CrisisDataCollector:
    def __init__(self):
        self.newsapi_key = os.getenv("NEWSAPI_KEY")
        self.mediastack_key = os.getenv("MEDIASTACK_KEY")
        self.newsdata_key = os.getenv("NEWSDATA_KEY")
        self.weatherstack_key = os.getenv("WEATHERSTACK_KEY")
        
        self.crisis_keywords = [
            'flood', 'earthquake', 'cyclone', 'tsunami', 'fire', 'drought', 
            'landslide', 'disaster', 'emergency', 'evacuation', 'rescue', 
            'storm', 'hurricane', 'accident', 'explosion', 'collapse'
        ]
        
        self.indian_cities = list(INDIAN_COORDINATES.keys())
        self.indian_states = list(INDIAN_STATES.keys())
    
    def test_api_connections(self):
        """Test all API connections and return status"""
        status = {}
        
        # Test NewsAPI
        if self.newsapi_key:
            try:
                response = requests.get(
                    f"https://newsapi.org/v2/top-headlines?country=in&apiKey={self.newsapi_key}",
                    timeout=10
                )
                status['NewsAPI'] = 'Connected' if response.status_code == 200 else f'Error {response.status_code}'
                logger.info(f"NewsAPI Status: {status['NewsAPI']}")
            except Exception as e:
                status['NewsAPI'] = f'Connection Failed'
                logger.error(f"NewsAPI Error: {e}")
        else:
            status['NewsAPI'] = 'No API Key'
        
        # Test MediaStack
        if self.mediastack_key:
            try:
                response = requests.get(
                    f"http://api.mediastack.com/v1/news?access_key={self.mediastack_key}&countries=in&limit=1",
                    timeout=10
                )
                status['MediaStack'] = 'Connected' if response.status_code == 200 else f'Error {response.status_code}'
                logger.info(f"MediaStack Status: {status['MediaStack']}")
            except Exception as e:
                status['MediaStack'] = f'Connection Failed'
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
                status['NewsData.io'] = 'Connected' if response.status_code == 200 else f'Error {response.status_code}'
                logger.info(f"NewsData.io Status: {status['NewsData.io']}")
            except Exception as e:
                status['NewsData.io'] = f'Connection Failed'
                logger.error(f"NewsData.io Error: {e}")
        else:
            status['NewsData.io'] = 'No API Key'
        
        # Test Weatherstack
        if self.weatherstack_key:
            try:
                response = requests.get(
                    f"http://api.weatherstack.com/current?access_key={self.weatherstack_key}&query=Delhi",
                    timeout=10
                )
                status['Weatherstack'] = 'Connected' if response.status_code == 200 else f'Error {response.status_code}'
                logger.info(f"Weatherstack Status: {status['Weatherstack']}")
            except Exception as e:
                status['Weatherstack'] = f'Connection Failed'
                logger.error(f"Weatherstack Error: {e}")
        else:
            status['Weatherstack'] = 'No API Key'
        
        return status
    
    def collect_crisis_news(self):
        """Collect crisis-related news from multiple APIs"""
        all_news = []
        
        # NewsAPI Collection
        if self.newsapi_key:
            try:
                for keyword in self.crisis_keywords[:5]:  # Limit for free tier
                    response = requests.get(
                        f"https://newsapi.org/v2/everything?q={keyword} India&sortBy=publishedAt&pageSize=10&apiKey={self.newsapi_key}",
                        timeout=10
                    )
                    
                    if response.status_code == 200:
                        data = response.json()
                        for article in data.get('articles', []):
                            if self._is_india_related(article.get('title', '') + ' ' + article.get('description', '')):
                                location = self._extract_location(article.get('title', '') + ' ' + article.get('description', ''))
                                coords = self._get_coordinates(location)
                                
                                crisis_info = self._classify_crisis(article.get('title', '') + ' ' + article.get('description', ''))
                                
                                news_item = {
                                    'title': article.get('title', ''),
                                    'description': article.get('description', ''),
                                    'source': article.get('source', {}).get('name', 'NewsAPI'),
                                    'published_at': article.get('publishedAt', ''),
                                    'url': article.get('url', ''),
                                    'location': location,
                                    'latitude': coords[0],
                                    'longitude': coords[1],
                                    'crisis_type': crisis_info['type'],
                                    'severity': crisis_info['severity'],
                                    'confidence': crisis_info['confidence']
                                }
                                all_news.append(news_item)
                    
                    time.sleep(0.5)  # Rate limiting
                    
                logger.info(f"Collected {len([n for n in all_news if 'NewsAPI' in n['source']])} articles from NewsAPI")
            except Exception as e:
                logger.error(f"NewsAPI collection error: {e}")
        
        # MediaStack Collection
        if self.mediastack_key:
            try:
                response = requests.get(
                    f"http://api.mediastack.com/v1/news?access_key={self.mediastack_key}&countries=in&keywords={'|'.join(self.crisis_keywords[:10])}&limit=20",
                    timeout=10
                )
                
                if response.status_code == 200:
                    data = response.json()
                    for article in data.get('data', []):
                        if self._is_india_related(article.get('title', '') + ' ' + article.get('description', '')):
                            location = self._extract_location(article.get('title', '') + ' ' + article.get('description', ''))
                            coords = self._get_coordinates(location)
                            
                            crisis_info = self._classify_crisis(article.get('title', '') + ' ' + article.get('description', ''))
                            
                            news_item = {
                                'title': article.get('title', ''),
                                'description': article.get('description', ''),
                                'source': 'MediaStack',
                                'published_at': article.get('published_at', ''),
                                'url': article.get('url', ''),
                                'location': location,
                                'latitude': coords[0],
                                'longitude': coords[1],
                                'crisis_type': crisis_info['type'],
                                'severity': crisis_info['severity'],
                                'confidence': crisis_info['confidence']
                            }
                            all_news.append(news_item)
                
                logger.info(f"Collected articles from MediaStack")
            except Exception as e:
                logger.error(f"MediaStack collection error: {e}")
        
        return all_news
    
    def collect_weather_alerts(self):
        """Collect weather alerts for major Indian cities"""
        weather_data = []
        major_cities = ['Delhi', 'Mumbai', 'Bangalore', 'Chennai', 'Kolkata', 'Hyderabad']
        
        if self.weatherstack_key:
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
                        
                        # Check for extreme conditions
                        if (temperature > 45 or temperature < 0 or wind_speed > 60 or 
                            any(extreme in weather_desc for extreme in ['storm', 'heavy', 'severe', 'extreme'])):
                            
                            severity = 'high' if temperature > 45 or wind_speed > 80 else 'medium'
                            
                            alert = {
                                'city': location.get('name', city),
                                'temperature': temperature,
                                'description': weather_desc,
                                'wind_speed': wind_speed,
                                'severity': severity,
                                'latitude': location.get('lat', INDIAN_COORDINATES.get(city.lower(), (20.5937, 78.9629))[0]),
                                'longitude': location.get('lon', INDIAN_COORDINATES.get(city.lower(), (20.5937, 78.9629))[1]),
                                'timestamp': datetime.now().isoformat()
                            }
                            weather_data.append(alert)
                    
                    time.sleep(1)  # Rate limiting
                except Exception as e:
                    logger.error(f"Weather API error for {city}: {e}")
        
        return weather_data
    
    def _is_india_related(self, text):
        """Check if text is related to India"""
        text_lower = text.lower()
        india_terms = ['india', 'indian', 'delhi', 'mumbai', 'bangalore', 'chennai', 'kolkata', 'hyderabad']
        return any(term in text_lower for term in india_terms + self.indian_cities + [s.lower() for s in self.indian_states])
    
    def _extract_location(self, text):
        """Extract location from text"""
        text_lower = text.lower()
        
        # Check cities first
        for city in self.indian_cities:
            if city in text_lower:
                return city.title()
        
        # Check states
        for state in self.indian_states:
            if state.lower() in text_lower:
                return state
        
        return None
    
    def _get_coordinates(self, location):
        """Get coordinates for a location"""
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
    
    def _classify_crisis(self, text):
        """Simple crisis classification"""
        text_lower = text.lower()
        
        # Crisis type classification
        if any(word in text_lower for word in ['flood', 'flooding', 'inundation']):
            crisis_type = 'flood'
        elif any(word in text_lower for word in ['earthquake', 'quake', 'tremor']):
            crisis_type = 'earthquake'
        elif any(word in text_lower for word in ['cyclone', 'hurricane', 'typhoon']):
            crisis_type = 'cyclone'
        elif any(word in text_lower for word in ['fire', 'wildfire', 'blaze']):
            crisis_type = 'fire'
        elif any(word in text_lower for word in ['drought', 'water shortage']):
            crisis_type = 'drought'
        elif any(word in text_lower for word in ['landslide', 'mudslide']):
            crisis_type = 'landslide'
        elif any(word in text_lower for word in ['storm', 'thunderstorm']):
            crisis_type = 'storm'
        else:
            crisis_type = 'accident'
        
        # Severity classification
        if any(word in text_lower for word in ['severe', 'massive', 'devastating', 'major', 'critical']):
            severity = 'high'
        elif any(word in text_lower for word in ['moderate', 'significant', 'considerable']):
            severity = 'medium'
        else:
            severity = 'low'
        
        # Confidence based on keyword matches
        crisis_indicators = sum(1 for word in self.crisis_keywords if word in text_lower)
        confidence = min(0.5 + (crisis_indicators * 0.1), 1.0)
        
        return {
            'type': crisis_type,
            'severity': severity,
            'confidence': confidence
        }

class SMSManager:
    def __init__(self):
        self.twilio_sid = os.getenv("TWILIO_ACCOUNT_SID")
        self.twilio_token = os.getenv("TWILIO_AUTH_TOKEN")
        self.twilio_phone = os.getenv("TWILIO_PHONE_NUMBER")
        
        self.client = None
        if self.twilio_sid and self.twilio_token:
            try:
                from twilio.rest import Client
                self.client = Client(self.twilio_sid, self.twilio_token)
                logger.info("Twilio client initialized successfully")
            except Exception as e:
                logger.error(f"Twilio initialization error: {e}")
    
    def register_user(self, phone_number, location, alert_radius=50, language='English'):
        """Register user for SMS alerts"""
        try:
            # Store in simple database
            conn = sqlite3.connect('sms_users.db')
            cursor = conn.cursor()
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY,
                    phone TEXT UNIQUE,
                    location TEXT,
                    radius INTEGER,
                    language TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            cursor.execute('''
                INSERT OR REPLACE INTO users (phone, location, radius, language)
                VALUES (?, ?, ?, ?)
            ''', (phone_number, location, alert_radius, language))
            
            conn.commit()
            conn.close()
            
            logger.info(f"User registered: {phone_number} for {location}")
            return True
        except Exception as e:
            logger.error(f"Registration error: {e}")
            return False
    
    def send_alert(self, phone_number, message):
        """Send SMS alert"""
        if not self.client:
            logger.warning("Twilio client not available")
            return False
        
        try:
            message_obj = self.client.messages.create(
                body=message,
                from_=self.twilio_phone,
                to=phone_number
            )
            logger.info(f"SMS sent to {phone_number}: {message_obj.sid}")
            return True
        except Exception as e:
            logger.error(f"SMS sending error: {e}")
            return False

def create_india_map_visualization(crisis_data, weather_data):
    """Create interactive map visualization using Plotly"""
    fig = go.Figure()
    
    # Add crisis markers
    if crisis_data:
        df_crisis = pd.DataFrame(crisis_data)
        
        # Color mapping for severity
        color_map = {'high': 'red', 'medium': 'orange', 'low': 'yellow'}
        
        for severity in ['high', 'medium', 'low']:
            severity_data = df_crisis[df_crisis['severity'] == severity]
            if not severity_data.empty:
                fig.add_trace(go.Scattermapbox(
                    lat=severity_data['latitude'],
                    lon=severity_data['longitude'],
                    mode='markers',
                    marker=dict(
                        size=15 if severity == 'high' else 12 if severity == 'medium' else 10,
                        color=color_map[severity],
                        opacity=0.8
                    ),
                    text=severity_data.apply(lambda x: f"<b>{x['crisis_type'].title()}</b><br>"
                                                     f"Location: {x['location']}<br>"
                                                     f"Severity: {x['severity'].title()}<br>"
                                                     f"Source: {x['source']}", axis=1),
                    hovertemplate='%{text}<extra></extra>',
                    name=f'{severity.title()} Severity'
                ))
    
    # Add weather alerts
    if weather_data:
        df_weather = pd.DataFrame(weather_data)
        fig.add_trace(go.Scattermapbox(
            lat=df_weather['latitude'],
            lon=df_weather['longitude'],
            mode='markers',
            marker=dict(size=12, color='blue', opacity=0.7),
            text=df_weather.apply(lambda x: f"<b>Weather Alert</b><br>"
                                           f"City: {x['city']}<br>"
                                           f"Temperature: {x['temperature']}°C<br>"
                                           f"Wind: {x['wind_speed']} km/h", axis=1),
            hovertemplate='%{text}<extra></extra>',
            name='Weather Alerts'
        ))
    
    # Update layout
    fig.update_layout(
        mapbox=dict(
            style="open-street-map",
            center=dict(lat=20.5937, lon=78.9629),
            zoom=4
        ),
        height=600,
        margin=dict(l=0, r=0, t=0, b=0),
        showlegend=True
    )
    
    return fig

def create_analytics_charts(crisis_data):
    """Create analytics charts"""
    if not crisis_data:
        return None, None, None
    
    df = pd.DataFrame(crisis_data)
    
    # Crisis type distribution
    type_counts = df['crisis_type'].value_counts()
    fig_pie = px.pie(
        values=type_counts.values,
        names=type_counts.index,
        title="Crisis Types Distribution",
        color_discrete_sequence=px.colors.qualitative.Set3
    )
    fig_pie.update_layout(height=400)
    
    # Severity distribution
    severity_counts = df['severity'].value_counts()
    color_map = {'high': '#FF6B6B', 'medium': '#FFB347', 'low': '#87CEEB'}
    colors = [color_map.get(severity, '#999999') for severity in severity_counts.index]
    
    fig_bar = px.bar(
        x=severity_counts.index,
        y=severity_counts.values,
        title="Severity Levels",
        color=severity_counts.index,
        color_discrete_map=color_map
    )
    fig_bar.update_layout(height=400, showlegend=False)
    
    # Location-based analysis
    location_counts = df['location'].value_counts().head(10)
    fig_location = px.bar(
        x=location_counts.values,
        y=location_counts.index,
        orientation='h',
        title="Top 10 Affected Locations",
        color=location_counts.values,
        color_continuous_scale='Reds'
    )
    fig_location.update_layout(height=400)
    
    return fig_pie, fig_bar, fig_location

def main():
    """Main application function"""
    load_custom_css()
    
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>🚨 CrisisRadar</h1>
        <h3>Real-Time Crisis Detection & Emergency Response System for India</h3>
        <p>Powered by AI • Multi-Source Data Integration • 24/7 Monitoring</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Initialize systems
    if 'data_collector' not in st.session_state:
        st.session_state.data_collector = CrisisDataCollector()
        st.session_state.sms_manager = SMSManager()
        st.session_state.crisis_data = []
        st.session_state.weather_data = []
        st.session_state.last_update = None
    
    # Sidebar
    with st.sidebar:
        st.markdown("### 🎛️ Control Panel")
        
        # API Status Check
        if st.button("🔍 Check API Status"):
            with st.spinner("Testing API connections..."):
                api_status = st.session_state.data_collector.test_api_connections()
                
                st.markdown("#### API Connection Status")
                for api, status in api_status.items():
                    if 'Connected' in status:
                        st.markdown(f"✅ **{api}**: <span class='status-online'>{status}</span>", unsafe_allow_html=True)
                    else:
                        st.markdown(f"❌ **{api}**: <span class='status-offline'>{status}</span>", unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Data Refresh
        auto_refresh = st.checkbox("🔄 Auto-refresh (30s)", value=False)
        
        if st.button("📡 Refresh Data Now"):
            with st.spinner("Collecting latest crisis data..."):
                try:
                    st.session_state.crisis_data = st.session_state.data_collector.collect_crisis_news()
                    st.session_state.weather_data = st.session_state.data_collector.collect_weather_alerts()
                    st.session_state.last_update = datetime.now()
                    st.success(f"Data updated! Found {len(st.session_state.crisis_data)} crisis reports")
                except Exception as e:
                    st.error("Data collection failed. Check API keys.")
                    logger.error(f"Data collection error: {e}")
        
        st.markdown("---")
        
        # Language Selection
        language = st.selectbox(
            "🌐 Language",
            ["English", "हिंदी (Hindi)", "বাংলা (Bengali)", "தமிழ் (Tamil)", "తెలుగు (Telugu)", "मराठी (Marathi)"]
        )
        
        # Crisis Filters
        st.markdown("#### 🎯 Crisis Filters")
        crisis_types = st.multiselect(
            "Crisis Types",
            ["flood", "earthquake", "cyclone", "fire", "drought", "landslide", "storm", "accident"],
            default=["flood", "earthquake", "cyclone"]
        )
        
        severity_filter = st.multiselect(
            "Severity Levels",
            ["high", "medium", "low"],
            default=["high", "medium", "low"]
        )
        
        st.markdown("---")
        
        # SMS Alert Registration
        st.markdown("#### 📱 SMS Alert Registration")
        phone = st.text_input("📞 Phone (+91XXXXXXXXXX)")
        location = st.selectbox("📍 Your Location", list(INDIAN_STATES.keys()) + list(INDIAN_COORDINATES.keys()))
        radius = st.slider("Alert Radius (km)", 10, 500, 50)
        
        if st.button("🔔 Register for Alerts"):
            if phone and location:
                success = st.session_state.sms_manager.register_user(phone, location, radius, language)
                if success:
                    st.success("✅ Successfully registered for SMS alerts!")
                else:
                    st.error("❌ Registration failed")
            else:
                st.error("Please provide phone number and location")
    
    # Main Dashboard
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_crises = len(st.session_state.crisis_data)
        st.markdown(f"""
        <div class="metric-container">
            <h3>🚨 Active Crises</h3>
            <h2 style="color: #FF6B6B;">{total_crises}</h2>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        high_severity = len([c for c in st.session_state.crisis_data if c.get('severity') == 'high'])
        st.markdown(f"""
        <div class="metric-container">
            <h3>🔴 High Severity</h3>
            <h2 style="color: #FF4757;">{high_severity}</h2>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        weather_alerts = len(st.session_state.weather_data)
        st.markdown(f"""
        <div class="metric-container">
            <h3>🌩️ Weather Alerts</h3>
            <h2 style="color: #3742FA;">{weather_alerts}</h2>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        last_update = st.session_state.last_update
        update_text = last_update.strftime("%H:%M:%S") if last_update else "Never"
        st.markdown(f"""
        <div class="metric-container">
            <h3>🕐 Last Update</h3>
            <h2 style="color: #2ED573;">{update_text}</h2>
        </div>
        """, unsafe_allow_html=True)
    
    # Main Content Tabs
    tab1, tab2, tab3, tab4 = st.tabs(["🗺️ Crisis Map", "📊 Analytics", "📰 Latest Alerts", "🏥 Emergency Info"])
    
    with tab1:
        st.markdown("### 🗺️ Real-Time Crisis Map of India")
        
        # Filter data
        filtered_data = st.session_state.crisis_data
        if crisis_types:
            filtered_data = [c for c in filtered_data if c.get('crisis_type') in crisis_types]
        if severity_filter:
            filtered_data = [c for c in filtered_data if c.get('severity') in severity_filter]
        
        # Create and display map
        if filtered_data or st.session_state.weather_data:
            map_fig = create_india_map_visualization(filtered_data, st.session_state.weather_data)
            st.plotly_chart(map_fig, use_container_width=True)
        else:
            st.info("No crisis data to display. Click 'Refresh Data Now' to collect latest information.")
    
    with tab2:
        st.markdown("### 📊 Crisis Analytics Dashboard")
        
        if st.session_state.crisis_data:
            col1, col2 = st.columns(2)
            
            pie_fig, bar_fig, location_fig = create_analytics_charts(st.session_state.crisis_data)
            
            with col1:
                if pie_fig:
                    st.plotly_chart(pie_fig, use_container_width=True)
                if location_fig:
                    st.plotly_chart(location_fig, use_container_width=True)
            
            with col2:
                if bar_fig:
                    st.plotly_chart(bar_fig, use_container_width=True)
                
                # Statistics table
                df = pd.DataFrame(st.session_state.crisis_data)
                stats = {
                    "Total Reports": len(df),
                    "Unique Locations": df['location'].nunique(),
                    "Avg Confidence": f"{df['confidence'].mean():.2f}",
                    "Most Common Type": df['crisis_type'].mode().iloc[0] if not df.empty else "N/A"
                }
                
                st.markdown("#### 📈 Key Statistics")
                for key, value in stats.items():
                    st.metric(key, value)
        else:
            st.info("No data available for analytics. Please refresh data first.")
    
    with tab3:
        st.markdown("### 📰 Latest Crisis Alerts")
        
        if st.session_state.crisis_data:
            for i, alert in enumerate(st.session_state.crisis_data[:10]):
                severity_color = {"high": "#FF6B6B", "medium": "#FFB347", "low": "#87CEEB"}
                color = severity_color.get(alert.get('severity', 'low'), '#999999')
                
                st.markdown(f"""
                <div class="crisis-card" style="border-left: 5px solid {color};">
                    <h4>{alert.get('title', 'Crisis Alert')}</h4>
                    <p><strong>Type:</strong> {alert.get('crisis_type', 'Unknown').title()} | 
                       <strong>Severity:</strong> {alert.get('severity', 'Unknown').title()} | 
                       <strong>Location:</strong> {alert.get('location', 'Unknown')}</p>
                    <p>{alert.get('description', 'No description available')}</p>
                    <p><small><strong>Source:</strong> {alert.get('source', 'Unknown')} | 
                              <strong>Confidence:</strong> {alert.get('confidence', 0):.0%}</small></p>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No recent alerts available. Click 'Refresh Data Now' to get latest updates.")
    
    with tab4:
        st.markdown("### 🏥 Emergency Resources & Contacts")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("""
            <div class="emergency-card">
                <h4>🚨 Emergency Numbers</h4>
                <p><strong>Police:</strong> 100</p>
                <p><strong>Fire:</strong> 101</p>
                <p><strong>Ambulance:</strong> 108</p>
                <p><strong>Disaster Management:</strong> 1078</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div class="emergency-card">
                <h4>🏥 Helplines</h4>
                <p><strong>Women Helpline:</strong> 1091</p>
                <p><strong>Child Helpline:</strong> 1098</p>
                <p><strong>Senior Citizen:</strong> 14567</p>
                <p><strong>Tourist Helpline:</strong> 1363</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown("""
            <div class="emergency-card">
                <h4>🚂 Transport Emergency</h4>
                <p><strong>Railway:</strong> 1072</p>
                <p><strong>Road Accident:</strong> 1073</p>
                <p><strong>Highway:</strong> 1033</p>
                <p><strong>Aviation:</strong> 1678</p>
            </div>
            """, unsafe_allow_html=True)
        
        # Emergency Preparedness Tips
        st.markdown("#### 🎯 Emergency Preparedness Tips")
        tips = [
            "Keep emergency numbers saved in your phone",
            "Maintain a first aid kit at home and workplace", 
            "Know evacuation routes in your building and area",
            "Keep important documents in waterproof containers",
            "Store 3 days worth of water and non-perishable food",
            "Have a battery-powered radio for emergency updates"
        ]
        
        for tip in tips:
            st.markdown(f"• {tip}")
    
    # Auto-refresh functionality
    if auto_refresh:
        time.sleep(30)
        st.rerun()
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #666; padding: 1rem;">
        <p><strong>CrisisRadar v2.0</strong> - Protecting India with Real-Time Crisis Intelligence</p>
        <p>Built with ❤️ for India | Powered by Multiple APIs | AI-Driven Detection</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()