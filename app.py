import streamlit as st
import folium
from streamlit_folium import st_folium
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import time
from datetime import datetime, timedelta
import threading
import schedule
from data_collector import DataCollector
from ml_classifier import CrisisClassifier
from sms_alerts import SMSAlerter
from utils import load_config, format_datetime
from india_data import IndiaData
from language_processor import LanguageProcessor
from database import CrisisDatabase
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure page
st.set_page_config(
    page_title="CrisisRadar - India Crisis Detection System",
    page_icon="🚨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'initialized' not in st.session_state:
    st.session_state.initialized = False
    st.session_state.data_collector = None
    st.session_state.classifier = None
    st.session_state.sms_alerter = None
    st.session_state.language_processor = None
    st.session_state.database = None
    st.session_state.india_data = None
    st.session_state.last_update = None
    st.session_state.crisis_data = pd.DataFrame()
    st.session_state.weather_alerts = pd.DataFrame()
    st.session_state.auto_refresh = False

@st.cache_resource
def initialize_system():
    """Initialize all system components"""
    try:
        # Initialize components
        data_collector = DataCollector()
        classifier = CrisisClassifier()
        sms_alerter = SMSAlerter()
        language_processor = LanguageProcessor()
        database = CrisisDatabase()
        india_data = IndiaData()
        
        return data_collector, classifier, sms_alerter, language_processor, database, india_data
    except Exception as e:
        st.error(f"Failed to initialize system: {str(e)}")
        return None, None, None, None, None, None

def update_data():
    """Update crisis data from all sources"""
    if not st.session_state.initialized:
        return
    
    try:
        with st.spinner("🔄 Updating crisis data..."):
            # Collect data from all sources
            news_data = st.session_state.data_collector.collect_news_data()
            weather_data = st.session_state.data_collector.collect_weather_alerts()
            rss_data = st.session_state.data_collector.collect_rss_feeds()
            
            # Combine all data
            all_data = news_data + rss_data
            
            # Classify crises
            classified_data = []
            for item in all_data:
                crisis_info = st.session_state.classifier.classify_crisis(item['text'], item['location'])
                if crisis_info['is_crisis']:
                    item.update(crisis_info)
                    classified_data.append(item)
            
            # Convert to DataFrame
            if classified_data:
                st.session_state.crisis_data = pd.DataFrame(classified_data)
            else:
                st.session_state.crisis_data = pd.DataFrame()
            
            if weather_data:
                st.session_state.weather_alerts = pd.DataFrame(weather_data)
            else:
                st.session_state.weather_alerts = pd.DataFrame()
            
            # Store in database
            st.session_state.database.store_crisis_data(classified_data)
            st.session_state.database.store_weather_data(weather_data)
            
            st.session_state.last_update = datetime.now()
            
    except Exception as e:
        st.error(f"Error updating data: {str(e)}")

def create_india_map(crisis_data, weather_data):
    """Create interactive map of India with crisis markers"""
    # Create base map centered on India
    india_map = folium.Map(
        location=[20.5937, 78.9629],  # Center of India
        zoom_start=5,
        tiles='OpenStreetMap'
    )
    
    # Add crisis markers
    if not crisis_data.empty:
        for idx, row in crisis_data.iterrows():
            # Determine marker color based on severity
            color = {
                'high': 'red',
                'medium': 'orange', 
                'low': 'yellow'
            }.get(row.get('severity', 'low'), 'blue')
            
            # Create popup content
            popup_content = f"""
            <b>{row.get('title', 'Crisis Alert')}</b><br>
            <b>Type:</b> {row.get('crisis_type', 'Unknown')}<br>
            <b>Severity:</b> {row.get('severity', 'Unknown')}<br>
            <b>Location:</b> {row.get('location', 'Unknown')}<br>
            <b>Time:</b> {row.get('published_at', 'Unknown')}<br>
            <b>Source:</b> {row.get('source', 'Unknown')}<br>
            """
            
            folium.Marker(
                location=[row.get('latitude', 20.5937), row.get('longitude', 78.9629)],
                popup=folium.Popup(popup_content, max_width=300),
                tooltip=f"{row.get('crisis_type', 'Crisis')} - {row.get('location', 'Unknown')}",
                icon=folium.Icon(color=color, icon='warning-sign', prefix='fa')
            ).add_to(india_map)
    
    # Add weather alert markers
    if not weather_data.empty:
        for idx, row in weather_data.iterrows():
            folium.Marker(
                location=[row.get('latitude', 20.5937), row.get('longitude', 78.9629)],
                popup=folium.Popup(f"<b>Weather Alert</b><br>{row.get('description', '')}", max_width=300),
                tooltip=f"Weather: {row.get('type', 'Alert')}",
                icon=folium.Icon(color='blue', icon='cloud', prefix='fa')
            ).add_to(india_map)
    
    # Add state boundaries and emergency resources
    states_data = st.session_state.india_data.get_state_boundaries()
    for state in states_data:
        folium.GeoJson(
            state['boundary'],
            style_function=lambda x: {
                'fillColor': 'transparent',
                'color': 'black',
                'weight': 1,
                'fillOpacity': 0.1
            },
            popup=folium.Popup(f"<b>{state['name']}</b>", max_width=200),
            tooltip=state['name']
        ).add_to(india_map)
    
    return india_map

def display_dashboard():
    """Main dashboard display"""
    st.title("🚨 CrisisRadar - India Crisis Detection System")
    st.markdown("*Real-time monitoring of natural disasters and emergencies across India*")
    
    # Sidebar controls
    with st.sidebar:
        st.header("🔧 Control Panel")
        
        # Auto-refresh toggle
        auto_refresh = st.checkbox("🔄 Auto Refresh (30s)", value=st.session_state.auto_refresh)
        st.session_state.auto_refresh = auto_refresh
        
        # Manual refresh button
        if st.button("📡 Refresh Data Now", use_container_width=True):
            update_data()
            st.rerun()
        
        # Language selection
        selected_language = st.selectbox(
            "🌐 Language / भाषा",
            ["English", "Hindi", "Bengali", "Tamil", "Telugu", "Marathi"],
            index=0
        )
        
        # Crisis type filter
        crisis_types = ["All", "Flood", "Earthquake", "Cyclone", "Fire", "Drought", "Landslide"]
        selected_crisis = st.multiselect(
            "🏷️ Filter Crisis Types",
            crisis_types,
            default=["All"]
        )
        
        # Severity filter
        severity_filter = st.multiselect(
            "⚠️ Severity Level",
            ["High", "Medium", "Low"],
            default=["High", "Medium", "Low"]
        )
        
        # SMS Alert Settings
        st.subheader("📱 SMS Alert Settings")
        phone_number = st.text_input("📞 Phone Number (+91XXXXXXXXXX)")
        alert_radius = st.slider("📍 Alert Radius (km)", 10, 500, 50)
        
        if st.button("🔔 Enable SMS Alerts", use_container_width=True):
            if phone_number:
                try:
                    st.session_state.sms_alerter.register_user(phone_number, alert_radius)
                    st.success("SMS alerts enabled!")
                except Exception as e:
                    st.error(f"Failed to enable SMS alerts: {str(e)}")
    
    # Main content area
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_crises = len(st.session_state.crisis_data) if not st.session_state.crisis_data.empty else 0
        st.metric("🚨 Active Crises", total_crises)
    
    with col2:
        high_severity = len(st.session_state.crisis_data[
            st.session_state.crisis_data['severity'] == 'high'
        ]) if not st.session_state.crisis_data.empty else 0
        st.metric("🔴 High Severity", high_severity)
    
    with col3:
        weather_alerts = len(st.session_state.weather_alerts) if not st.session_state.weather_alerts.empty else 0
        st.metric("🌩️ Weather Alerts", weather_alerts)
    
    with col4:
        last_update = st.session_state.last_update
        if last_update:
            st.metric("🕐 Last Update", last_update.strftime("%H:%M:%S"))
        else:
            st.metric("🕐 Last Update", "Never")
    
    # Create two main columns for map and analytics
    map_col, analytics_col = st.columns([2, 1])
    
    with map_col:
        st.subheader("🗺️ Crisis Map - India")
        
        # Filter data based on selections
        filtered_crisis_data = st.session_state.crisis_data.copy() if not st.session_state.crisis_data.empty else pd.DataFrame()
        
        if not filtered_crisis_data.empty:
            # Apply crisis type filter
            if "All" not in selected_crisis:
                filtered_crisis_data = filtered_crisis_data[
                    filtered_crisis_data['crisis_type'].isin([ct.lower() for ct in selected_crisis])
                ]
            
            # Apply severity filter
            filtered_crisis_data = filtered_crisis_data[
                filtered_crisis_data['severity'].isin([s.lower() for s in severity_filter])
            ]
        
        # Create and display map
        india_map = create_india_map(filtered_crisis_data, st.session_state.weather_alerts)
        map_data = st_folium(india_map, width=700, height=500)
    
    with analytics_col:
        st.subheader("📊 Crisis Analytics")
        
        if not st.session_state.crisis_data.empty:
            # Crisis type distribution
            crisis_counts = st.session_state.crisis_data['crisis_type'].value_counts()
            fig_pie = px.pie(
                values=crisis_counts.values,
                names=crisis_counts.index,
                title="Crisis Types Distribution"
            )
            fig_pie.update_layout(height=300)
            st.plotly_chart(fig_pie, use_container_width=True)
            
            # Severity distribution
            severity_counts = st.session_state.crisis_data['severity'].value_counts()
            fig_bar = px.bar(
                x=severity_counts.index,
                y=severity_counts.values,
                title="Severity Levels",
                color=severity_counts.index,
                color_discrete_map={'high': 'red', 'medium': 'orange', 'low': 'yellow'}
            )
            fig_bar.update_layout(height=300)
            st.plotly_chart(fig_bar, use_container_width=True)
        else:
            st.info("No crisis data available for analytics")
    
    # Recent Alerts Section
    st.subheader("📋 Recent Crisis Alerts")
    
    if not st.session_state.crisis_data.empty:
        # Display recent alerts in an expandable format
        recent_alerts = st.session_state.crisis_data.head(10)
        
        for idx, alert in recent_alerts.iterrows():
            with st.expander(f"🚨 {alert.get('title', 'Crisis Alert')} - {alert.get('location', 'Unknown')}"):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write(f"**Type:** {alert.get('crisis_type', 'Unknown').title()}")
                    st.write(f"**Severity:** {alert.get('severity', 'Unknown').title()}")
                    st.write(f"**Location:** {alert.get('location', 'Unknown')}")
                
                with col2:
                    st.write(f"**Source:** {alert.get('source', 'Unknown')}")
                    st.write(f"**Published:** {alert.get('published_at', 'Unknown')}")
                    st.write(f"**Confidence:** {alert.get('confidence', 0):.2f}")
                
                st.write(f"**Description:** {alert.get('description', alert.get('text', 'No description available'))}")
                
                # Translate button
                if st.button(f"🌐 Translate to {selected_language}", key=f"translate_{idx}"):
                    if selected_language != "English":
                        translated_text = st.session_state.language_processor.translate_text(
                            alert.get('description', ''), selected_language
                        )
                        st.write(f"**Translated:** {translated_text}")
    else:
        st.info("No recent crisis alerts available")
    
    # Emergency Resources Section
    st.subheader("🏥 Emergency Resources")
    
    resource_col1, resource_col2, resource_col3 = st.columns(3)
    
    with resource_col1:
        st.write("**🏥 Hospitals**")
        hospitals = st.session_state.india_data.get_emergency_resources('hospital')
        if hospitals:
            for hospital in hospitals[:5]:
                st.write(f"• {hospital['name']} - {hospital['location']}")
        else:
            st.write("No hospital data available")
    
    with resource_col2:
        st.write("**👮 Police Stations**")
        police = st.session_state.india_data.get_emergency_resources('police')
        if police:
            for station in police[:5]:
                st.write(f"• {station['name']} - {station['location']}")
        else:
            st.write("No police station data available")
    
    with resource_col3:
        st.write("**🏠 Shelters**")
        shelters = st.session_state.india_data.get_emergency_resources('shelter')
        if shelters:
            for shelter in shelters[:5]:
                st.write(f"• {shelter['name']} - {shelter['location']}")
        else:
            st.write("No shelter data available")

def main():
    """Main application function"""
    # Initialize system if not done
    if not st.session_state.initialized:
        with st.spinner("🚀 Initializing CrisisRadar System..."):
            components = initialize_system()
            if all(components):
                (st.session_state.data_collector, st.session_state.classifier, 
                 st.session_state.sms_alerter, st.session_state.language_processor,
                 st.session_state.database, st.session_state.india_data) = components
                st.session_state.initialized = True
                update_data()  # Initial data load
            else:
                st.error("Failed to initialize system. Please check your API keys and try again.")
                return
    
    # Display dashboard
    display_dashboard()
    
    # Auto-refresh functionality
    if st.session_state.auto_refresh:
        time.sleep(30)
        update_data()
        st.rerun()

if __name__ == "__main__":
    main()
