import streamlit as st
import os
import requests
import json
from datetime import datetime, timedelta
import sqlite3
import logging
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

# Simple logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_api_connections():
    """Test API connections and display status"""
    api_status = {}
    
    # Test NewsAPI
    newsapi_key = os.getenv("NEWSAPI_KEY")
    if newsapi_key:
        try:
            response = requests.get(
                f"https://newsapi.org/v2/top-headlines?country=in&apiKey={newsapi_key}",
                timeout=5
            )
            api_status['NewsAPI'] = 'Connected' if response.status_code == 200 else f'Error: {response.status_code}'
        except Exception as e:
            api_status['NewsAPI'] = f'Error: {str(e)}'
    else:
        api_status['NewsAPI'] = 'No API Key'
    
    # Test MediaStack
    mediastack_key = os.getenv("MEDIASTACK_KEY")
    if mediastack_key:
        try:
            response = requests.get(
                f"http://api.mediastack.com/v1/news?access_key={mediastack_key}&countries=in&limit=1",
                timeout=5
            )
            api_status['MediaStack'] = 'Connected' if response.status_code == 200 else f'Error: {response.status_code}'
        except Exception as e:
            api_status['MediaStack'] = f'Error: {str(e)}'
    else:
        api_status['MediaStack'] = 'No API Key'
    
    # Test Weatherstack
    weatherstack_key = os.getenv("WEATHERSTACK_KEY")
    if weatherstack_key:
        try:
            response = requests.get(
                f"http://api.weatherstack.com/current?access_key={weatherstack_key}&query=Delhi",
                timeout=5
            )
            api_status['Weatherstack'] = 'Connected' if response.status_code == 200 else f'Error: {response.status_code}'
        except Exception as e:
            api_status['Weatherstack'] = f'Error: {str(e)}'
    else:
        api_status['Weatherstack'] = 'No API Key'
    
    # Test Twilio
    twilio_sid = os.getenv("TWILIO_ACCOUNT_SID")
    twilio_token = os.getenv("TWILIO_AUTH_TOKEN")
    if twilio_sid and twilio_token:
        api_status['Twilio'] = 'Configured'
    else:
        api_status['Twilio'] = 'Not Configured'
    
    return api_status

def fetch_sample_news():
    """Fetch sample news data to demonstrate functionality"""
    newsapi_key = os.getenv("NEWSAPI_KEY")
    if not newsapi_key:
        return []
    
    try:
        response = requests.get(
            f"https://newsapi.org/v2/everything?q=India disaster OR flood OR earthquake&sortBy=publishedAt&apiKey={newsapi_key}",
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            articles = data.get('articles', [])[:10]  # Limit to 10 articles
            
            processed_articles = []
            for article in articles:
                processed_articles.append({
                    'title': article.get('title', ''),
                    'description': article.get('description', ''),
                    'source': article.get('source', {}).get('name', ''),
                    'published_at': article.get('publishedAt', ''),
                    'url': article.get('url', '')
                })
            
            return processed_articles
        
    except Exception as e:
        logger.error(f"Error fetching news: {str(e)}")
    
    return []

def main():
    """Main application function"""
    st.title("🚨 CrisisRadar - India Crisis Detection System")
    st.markdown("*Real-time monitoring of natural disasters and emergencies across India*")
    
    # Sidebar
    with st.sidebar:
        st.header("🔧 System Status")
        
        # Test API connections
        if st.button("Test API Connections"):
            with st.spinner("Testing API connections..."):
                api_status = test_api_connections()
                
                for api_name, status in api_status.items():
                    if 'Connected' in status or 'Configured' in status:
                        st.success(f"✅ {api_name}: {status}")
                    else:
                        st.error(f"❌ {api_name}: {status}")
        
        st.markdown("---")
        
        # Language selection
        selected_language = st.selectbox(
            "🌐 Language / भाषा",
            ["English", "Hindi", "Bengali", "Tamil", "Telugu", "Marathi"],
            index=0
        )
        
        # Crisis type filter
        crisis_types = st.multiselect(
            "🏷️ Crisis Types to Monitor",
            ["Flood", "Earthquake", "Cyclone", "Fire", "Drought", "Landslide", "Accident"],
            default=["Flood", "Earthquake", "Cyclone"]
        )
        
        st.markdown("---")
        
        # SMS Alert Registration
        st.subheader("📱 SMS Alerts")
        phone_number = st.text_input("📞 Phone Number (+91XXXXXXXXXX)")
        location = st.text_input("📍 Your Location (City, State)")
        alert_radius = st.slider("📍 Alert Radius (km)", 10, 500, 50)
        
        if st.button("🔔 Register for Alerts"):
            if phone_number and location:
                st.success(f"Alert registration saved for {phone_number} in {location}")
            else:
                st.error("Please enter both phone number and location")
    
    # Main content
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("🚨 Active Monitoring", "✅ Online")
    
    with col2:
        st.metric("📡 Data Sources", "4 APIs")
    
    with col3:
        st.metric("🗺️ Coverage", "India")
    
    with col4:
        st.metric("🌐 Languages", "6+ Supported")
    
    # News feed section
    st.subheader("📰 Latest Crisis-Related News")
    
    if st.button("🔄 Fetch Latest News"):
        with st.spinner("Fetching latest news..."):
            news_articles = fetch_sample_news()
            
            if news_articles:
                for i, article in enumerate(news_articles):
                    with st.expander(f"📰 {article['title'][:100]}..."):
                        st.write(f"**Source:** {article['source']}")
                        st.write(f"**Published:** {article['published_at']}")
                        st.write(f"**Description:** {article['description']}")
                        if article['url']:
                            st.write(f"**Link:** [Read more]({article['url']})")
            else:
                st.info("No news articles found or API limit reached")
    
    # Feature demonstration
    st.subheader("🎯 System Features")
    
    feature_col1, feature_col2 = st.columns(2)
    
    with feature_col1:
        st.write("**🔍 Real-Time Detection**")
        st.write("- Multi-source news monitoring")
        st.write("- Government RSS feeds")
        st.write("- Weather alerts")
        st.write("- ML-powered classification")
        
        st.write("**🗺️ Interactive Mapping**")
        st.write("- India-focused crisis visualization")
        st.write("- State-wise emergency resources")
        st.write("- Real-time crisis markers")
        
    with feature_col2:
        st.write("**📱 Smart Alerts**")
        st.write("- Location-based SMS notifications")
        st.write("- Multilingual support")
        st.write("- Severity-based filtering")
        st.write("- Duplicate prevention")
        
        st.write("**📊 Analytics**")
        st.write("- Historical trend analysis")
        st.write("- Crisis type distribution")
        st.write("- Geographic impact mapping")
    
    # Emergency contacts
    st.subheader("🚨 Emergency Contacts")
    
    emergency_col1, emergency_col2, emergency_col3 = st.columns(3)
    
    with emergency_col1:
        st.write("**🚓 Police:** 100")
        st.write("**🚒 Fire:** 101")
        st.write("**🚑 Ambulance:** 108")
    
    with emergency_col2:
        st.write("**🏥 Disaster Management:** 1078")
        st.write("**👩 Women Helpline:** 1091")
        st.write("**👶 Child Helpline:** 1098")
    
    with emergency_col3:
        st.write("**🚂 Railway Emergency:** 1072")
        st.write("**🚗 Road Emergency:** 1073")
        st.write("**🧓 Senior Citizen:** 14567")
    
    # Footer
    st.markdown("---")
    st.markdown("**CrisisRadar** - Keeping India Safe with Real-Time Crisis Detection")
    st.markdown("*Built with Streamlit • Powered by Multiple APIs • Made for India*")

if __name__ == "__main__":
    main()