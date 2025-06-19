import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
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
    .sidebar .sidebar-content {
        background: linear-gradient(180deg, #667eea 0%, #764ba2 100%);
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

class CrisisDataManager:
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
        
        self.init_database()
    
    def init_database(self):
        """Initialize SQLite database"""
        try:
            conn = sqlite3.connect('crisis_radar.db')
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
        """Test all API connections"""
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
                status['NewsAPI'] = 'Connection Failed'
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
                status['MediaStack'] = 'Connection Failed'
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
                status['NewsData.io'] = 'Connection Failed'
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
                status['Weatherstack'] = 'Connection Failed'
                logger.error(f"Weatherstack Error: {e}")
        else:
            status['Weatherstack'] = 'No API Key'
        
        return status
    
    def collect_crisis_data(self):
        """Collect crisis data from APIs"""
        all_data = []
        
        # NewsAPI Collection
        if self.newsapi_key:
            try:
                for keyword in self.crisis_keywords[:3]:  # Limit for free tier
                    response = requests.get(
                        f"https://newsapi.org/v2/everything?q={keyword} India&sortBy=publishedAt&pageSize=5&apiKey={self.newsapi_key}",
                        timeout=10
                    )
                    
                    if response.status_code == 200:
                        data = response.json()
                        for article in data.get('articles', []):
                            if self._is_india_related(article.get('title', '') + ' ' + article.get('description', '')):
                                location = self._extract_location(article.get('title', '') + ' ' + article.get('description', ''))
                                coords = self._get_coordinates(location)
                                crisis_info = self._classify_crisis(article.get('title', '') + ' ' + article.get('description', ''))
                                
                                item = {
                                    'title': article.get('title', 'Crisis Alert'),
                                    'description': article.get('description', 'No description'),
                                    'source': article.get('source', {}).get('name', 'NewsAPI'),
                                    'url': article.get('url', ''),
                                    'location': location or 'India',
                                    'latitude': coords[0],
                                    'longitude': coords[1],
                                    'crisis_type': crisis_info['type'],
                                    'severity': crisis_info['severity'],
                                    'confidence': crisis_info['confidence']
                                }
                                all_data.append(item)
                    
                    time.sleep(0.5)  # Rate limiting
                    
                logger.info(f"Collected {len(all_data)} articles from NewsAPI")
            except Exception as e:
                logger.error(f"NewsAPI collection error: {e}")
        
        # Store in database
        self._store_crisis_data(all_data)
        return all_data
    
    def collect_weather_data(self):
        """Collect weather data for major cities"""
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
                                'longitude': location.get('lon', INDIAN_COORDINATES.get(city.lower(), (20.5937, 78.9629))[1])
                            }
                            weather_data.append(alert)
                    
                    time.sleep(1)  # Rate limiting
                except Exception as e:
                    logger.error(f"Weather API error for {city}: {e}")
        
        self._store_weather_data(weather_data)
        return weather_data
    
    def _store_crisis_data(self, data):
        """Store crisis data in database"""
        try:
            conn = sqlite3.connect('crisis_radar.db')
            cursor = conn.cursor()
            
            for item in data:
                cursor.execute('''
                    INSERT INTO crisis_events 
                    (title, description, crisis_type, severity, location, latitude, longitude, source, confidence)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    item['title'], item['description'], item['crisis_type'], 
                    item['severity'], item['location'], item['latitude'], 
                    item['longitude'], item['source'], item['confidence']
                ))
            
            conn.commit()
            conn.close()
            logger.info(f"Stored {len(data)} crisis events")
        except Exception as e:
            logger.error(f"Database storage error: {e}")
    
    def _store_weather_data(self, data):
        """Store weather data in database"""
        try:
            conn = sqlite3.connect('crisis_radar.db')
            cursor = conn.cursor()
            
            for item in data:
                cursor.execute('''
                    INSERT INTO weather_alerts 
                    (city, temperature, description, wind_speed, severity)
                    VALUES (?, ?, ?, ?, ?)
                ''', (
                    item['city'], item['temperature'], item['description'], 
                    item['wind_speed'], item['severity']
                ))
            
            conn.commit()
            conn.close()
            logger.info(f"Stored {len(data)} weather alerts")
        except Exception as e:
            logger.error(f"Weather storage error: {e}")
    
    def get_recent_data(self, hours=24):
        """Get recent crisis and weather data"""
        try:
            conn = sqlite3.connect('crisis_radar.db')
            cursor = conn.cursor()
            
            # Get recent crisis data
            cursor.execute('''
                SELECT * FROM crisis_events 
                WHERE timestamp >= datetime('now', '-{} hours')
                ORDER BY timestamp DESC
            '''.format(hours))
            
            crisis_rows = cursor.fetchall()
            crisis_data = []
            
            for row in crisis_rows:
                crisis_data.append({
                    'id': row[0], 'title': row[1], 'description': row[2],
                    'crisis_type': row[3], 'severity': row[4], 'location': row[5],
                    'latitude': row[6], 'longitude': row[7], 'source': row[8],
                    'confidence': row[9], 'timestamp': row[10]
                })
            
            # Get recent weather data
            cursor.execute('''
                SELECT * FROM weather_alerts 
                WHERE timestamp >= datetime('now', '-{} hours')
                ORDER BY timestamp DESC
            '''.format(hours))
            
            weather_rows = cursor.fetchall()
            weather_data = []
            
            for row in weather_rows:
                weather_data.append({
                    'id': row[0], 'city': row[1], 'temperature': row[2],
                    'description': row[3], 'wind_speed': row[4], 'severity': row[5],
                    'timestamp': row[6]
                })
            
            conn.close()
            return crisis_data, weather_data
            
        except Exception as e:
            logger.error(f"Data retrieval error: {e}")
            return [], []
    
    def register_sms_user(self, phone, location, radius=50, language='English'):
        """Register user for SMS alerts"""
        try:
            conn = sqlite3.connect('crisis_radar.db')
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
    
    def _is_india_related(self, text):
        """Check if text is related to India"""
        text_lower = text.lower()
        india_terms = ['india', 'indian', 'delhi', 'mumbai', 'bangalore', 'chennai', 'kolkata', 'hyderabad']
        cities = list(INDIAN_COORDINATES.keys())
        states = [s.lower() for s in INDIAN_STATES.keys()]
        return any(term in text_lower for term in india_terms + cities + states)
    
    def _extract_location(self, text):
        """Extract location from text"""
        text_lower = text.lower()
        
        # Check cities first
        for city in INDIAN_COORDINATES.keys():
            if city in text_lower:
                return city.title()
        
        # Check states
        for state in INDIAN_STATES.keys():
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
        """Classify crisis from text"""
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
        
        # Confidence calculation
        crisis_indicators = sum(1 for word in self.crisis_keywords if word in text_lower)
        confidence = min(0.5 + (crisis_indicators * 0.1), 1.0)
        
        return {
            'type': crisis_type,
            'severity': severity,
            'confidence': confidence
        }

def create_india_map(crisis_data, weather_data):
    """Create interactive map using Plotly"""
    fig = go.Figure()
    
    # Add crisis markers
    if crisis_data:
        for item in crisis_data:
            color = {'high': 'red', 'medium': 'orange', 'low': 'yellow'}.get(item['severity'], 'blue')
            size = {'high': 15, 'medium': 12, 'low': 10}.get(item['severity'], 8)
            
            fig.add_trace(go.Scattermapbox(
                lat=[item['latitude']],
                lon=[item['longitude']],
                mode='markers',
                marker=dict(size=size, color=color, opacity=0.8),
                text=f"<b>{item['crisis_type'].title()}</b><br>"
                     f"Location: {item['location']}<br>"
                     f"Severity: {item['severity'].title()}<br>"
                     f"Source: {item['source']}",
                hovertemplate='%{text}<extra></extra>',
                name=f"{item['severity'].title()} Crisis",
                showlegend=False
            ))
    
    # Add weather alerts
    if weather_data:
        for item in weather_data:
            city_coords = INDIAN_COORDINATES.get(item['city'].lower(), (20.5937, 78.9629))
            fig.add_trace(go.Scattermapbox(
                lat=[city_coords[0]],
                lon=[city_coords[1]],
                mode='markers',
                marker=dict(size=12, color='blue', opacity=0.7),
                text=f"<b>Weather Alert</b><br>"
                     f"City: {item['city']}<br>"
                     f"Temperature: {item['temperature']}°C<br>"
                     f"Wind: {item['wind_speed']} km/h",
                hovertemplate='%{text}<extra></extra>',
                name='Weather Alert',
                showlegend=False
            ))
    
    # Update layout
    fig.update_layout(
        mapbox=dict(
            style="open-street-map",
            center=dict(lat=20.5937, lon=78.9629),
            zoom=4
        ),
        height=600,
        margin=dict(l=0, r=0, t=0, b=0)
    )
    
    return fig

def create_analytics_charts(crisis_data):
    """Create analytics charts"""
    if not crisis_data:
        return None, None
    
    # Crisis type distribution
    type_counts = {}
    for item in crisis_data:
        crisis_type = item['crisis_type']
        type_counts[crisis_type] = type_counts.get(crisis_type, 0) + 1
    
    if type_counts:
        fig_pie = px.pie(
            values=list(type_counts.values()),
            names=list(type_counts.keys()),
            title="Crisis Types Distribution",
            color_discrete_sequence=px.colors.qualitative.Set3
        )
        fig_pie.update_layout(height=400)
    else:
        fig_pie = None
    
    # Severity distribution
    severity_counts = {}
    for item in crisis_data:
        severity = item['severity']
        severity_counts[severity] = severity_counts.get(severity, 0) + 1
    
    if severity_counts:
        color_map = {'high': '#FF6B6B', 'medium': '#FFB347', 'low': '#87CEEB'}
        colors = [color_map.get(sev, '#999999') for sev in severity_counts.keys()]
        
        fig_bar = px.bar(
            x=list(severity_counts.keys()),
            y=list(severity_counts.values()),
            title="Severity Levels",
            color=list(severity_counts.keys()),
            color_discrete_map=color_map
        )
        fig_bar.update_layout(height=400, showlegend=False)
    else:
        fig_bar = None
    
    return fig_pie, fig_bar

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
    
    # Initialize system
    if 'crisis_manager' not in st.session_state:
        st.session_state.crisis_manager = CrisisDataManager()
        st.session_state.crisis_data = []
        st.session_state.weather_data = []
        st.session_state.last_update = None
    
    # Sidebar
    with st.sidebar:
        st.markdown("### 🎛️ Control Panel")
        
        # API Status Check
        if st.button("🔍 Check API Status"):
            with st.spinner("Testing API connections..."):
                api_status = st.session_state.crisis_manager.test_api_connections()
                
                st.markdown("#### API Connection Status")
                for api, status in api_status.items():
                    if 'Connected' in status:
                        st.markdown(f"✅ **{api}**: <span class='status-online'>{status}</span>", unsafe_allow_html=True)
                    else:
                        st.markdown(f"❌ **{api}**: <span class='status-offline'>{status}</span>", unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Data Collection
        if st.button("📡 Collect Latest Data"):
            with st.spinner("Collecting crisis and weather data..."):
                try:
                    crisis_data = st.session_state.crisis_manager.collect_crisis_data()
                    weather_data = st.session_state.crisis_manager.collect_weather_data()
                    
                    st.session_state.crisis_data = crisis_data
                    st.session_state.weather_data = weather_data
                    st.session_state.last_update = datetime.now()
                    
                    st.success(f"Data collected! Found {len(crisis_data)} crisis reports and {len(weather_data)} weather alerts")
                except Exception as e:
                    st.error("Data collection failed. Please check API keys.")
                    logger.error(f"Data collection error: {e}")
        
        # Load recent data
        if st.button("📂 Load Recent Data"):
            crisis_data, weather_data = st.session_state.crisis_manager.get_recent_data()
            st.session_state.crisis_data = crisis_data
            st.session_state.weather_data = weather_data
            st.info(f"Loaded {len(crisis_data)} recent crisis events")
        
        st.markdown("---")
        
        # Language and Filters
        language = st.selectbox(
            "🌐 Language",
            ["English", "हिंदी (Hindi)", "বাংলা (Bengali)", "தமிழ் (Tamil)", "తెలుగు (Telugu)", "मराठी (Marathi)"]
        )
        
        crisis_filter = st.multiselect(
            "🎯 Crisis Types",
            ["flood", "earthquake", "cyclone", "fire", "drought", "landslide", "storm", "accident"],
            default=["flood", "earthquake", "cyclone"]
        )
        
        severity_filter = st.multiselect(
            "⚠️ Severity Levels",
            ["high", "medium", "low"],
            default=["high", "medium", "low"]
        )
        
        st.markdown("---")
        
        # SMS Registration
        st.markdown("#### 📱 SMS Alert Registration")
        phone = st.text_input("📞 Phone (+91XXXXXXXXXX)")
        location = st.selectbox("📍 Location", list(INDIAN_STATES.keys()) + list(INDIAN_COORDINATES.keys()))
        radius = st.slider("Alert Radius (km)", 10, 500, 50)
        
        if st.button("🔔 Register for Alerts"):
            if phone and location:
                success = st.session_state.crisis_manager.register_sms_user(phone, location, radius, language)
                if success:
                    st.success("Successfully registered for SMS alerts!")
                else:
                    st.error("Registration failed")
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
            <div class="metric-value" style="color: #FF4757;">{high_severity}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="metric-container">
            <div class="metric-label">🌩️ Weather Alerts</div>
            <div class="metric-value" style="color: #3742FA;">{weather_alerts}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="metric-container">
            <div class="metric-label">🕐 Last Update</div>
            <div class="metric-value" style="color: #2ED573; font-size: 1.5rem;">{last_update}</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Main Content Tabs
    tab1, tab2, tab3, tab4 = st.tabs(["🗺️ Crisis Map", "📊 Analytics", "📰 Latest Alerts", "🏥 Emergency Info"])
    
    with tab1:
        st.markdown("### 🗺️ Real-Time Crisis Map of India")
        
        # Filter data
        filtered_crisis = st.session_state.crisis_data
        if crisis_filter:
            filtered_crisis = [c for c in filtered_crisis if c.get('crisis_type') in crisis_filter]
        if severity_filter:
            filtered_crisis = [c for c in filtered_crisis if c.get('severity') in severity_filter]
        
        # Create and display map
        if filtered_crisis or st.session_state.weather_data:
            map_fig = create_india_map(filtered_crisis, st.session_state.weather_data)
            st.plotly_chart(map_fig, use_container_width=True)
            
            # Map legend
            st.markdown("""
            **Map Legend:**
            - 🔴 Red: High Severity Crisis
            - 🟠 Orange: Medium Severity Crisis  
            - 🟡 Yellow: Low Severity Crisis
            - 🔵 Blue: Weather Alert
            """)
        else:
            st.info("No crisis data to display. Click 'Collect Latest Data' to gather information.")
    
    with tab2:
        st.markdown("### 📊 Crisis Analytics Dashboard")
        
        if st.session_state.crisis_data:
            col1, col2 = st.columns(2)
            
            pie_fig, bar_fig = create_analytics_charts(st.session_state.crisis_data)
            
            with col1:
                if pie_fig:
                    st.plotly_chart(pie_fig, use_container_width=True)
            
            with col2:
                if bar_fig:
                    st.plotly_chart(bar_fig, use_container_width=True)
            
            # Statistics
            st.markdown("#### 📈 Key Statistics")
            
            unique_locations = len(set(c['location'] for c in st.session_state.crisis_data if c['location']))
            avg_confidence = sum(c['confidence'] for c in st.session_state.crisis_data) / len(st.session_state.crisis_data) if st.session_state.crisis_data else 0
            most_common_type = max(set(c['crisis_type'] for c in st.session_state.crisis_data), 
                                 key=lambda x: sum(1 for c in st.session_state.crisis_data if c['crisis_type'] == x)) if st.session_state.crisis_data else "N/A"
            
            metrics_col1, metrics_col2, metrics_col3, metrics_col4 = st.columns(4)
            
            with metrics_col1:
                st.metric("Total Reports", len(st.session_state.crisis_data))
            with metrics_col2:
                st.metric("Unique Locations", unique_locations)
            with metrics_col3:
                st.metric("Avg Confidence", f"{avg_confidence:.2f}")
            with metrics_col4:
                st.metric("Most Common Type", most_common_type.title())
        else:
            st.info("No data available for analytics. Please collect data first.")
    
    with tab3:
        st.markdown("### 📰 Latest Crisis Alerts")
        
        if st.session_state.crisis_data:
            for i, alert in enumerate(st.session_state.crisis_data[:10]):
                severity_colors = {"high": "#FF6B6B", "medium": "#FFB347", "low": "#87CEEB"}
                color = severity_colors.get(alert.get('severity', 'low'), '#999999')
                
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
            st.info("No recent alerts available. Click 'Collect Latest Data' to get updates.")
    
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
        
        # Emergency Preparedness
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