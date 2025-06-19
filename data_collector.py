import requests
import feedparser
import json
from datetime import datetime, timedelta
import os
from typing import List, Dict, Any
import time
import logging
from utils import get_coordinates, clean_text
import trafilatura

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DataCollector:
    def __init__(self):
        """Initialize data collector with API keys"""
        self.newsapi_key = os.getenv("NEWSAPI_KEY")
        self.mediastack_key = os.getenv("MEDIASTACK_KEY")
        self.newsdata_key = os.getenv("NEWSDATA_KEY")
        self.weatherstack_key = os.getenv("WEATHERSTACK_KEY")
        
        # Indian government and news RSS feeds
        self.rss_feeds = {
            'IMD': 'https://mausam.imd.gov.in/imd_latest/contents/all_warning.xml',
            'NDMA': 'http://ndma.gov.in/en/feeds/ndma-news.xml',
            'PIB': 'https://pib.gov.in/RssMain.aspx?ModId=5&Lang=1',
            'NDTV': 'https://feeds.feedburner.com/ndtvnews-india-news',
            'Times_of_India': 'https://timesofindia.indiatimes.com/rssfeedstopstories.cms',
            'Hindustan_Times': 'https://www.hindustantimes.com/feeds/rss/india-news/rssfeed.xml',
            'Indian_Express': 'https://indianexpress.com/section/india/feed/'
        }
        
        # Indian cities and states for location filtering
        self.indian_locations = [
            "Mumbai", "Delhi", "Bangalore", "Hyderabad", "Ahmedabad", "Chennai", "Kolkata",
            "Surat", "Pune", "Jaipur", "Lucknow", "Kanpur", "Nagpur", "Indore", "Thane",
            "Bhopal", "Visakhapatnam", "Pimpri-Chinchwad", "Patna", "Vadodara", "Ghaziabad",
            "Ludhiana", "Agra", "Nashik", "Faridabad", "Meerut", "Rajkot", "Kalyan-Dombivali",
            "Vasai-Virar", "Varanasi", "Srinagar", "Aurangabad", "Dhanbad", "Amritsar",
            "Navi Mumbai", "Allahabad", "Ranchi", "Howrah", "Coimbatore", "Jabalpur",
            "Maharashtra", "Uttar Pradesh", "Bihar", "West Bengal", "Madhya Pradesh",
            "Tamil Nadu", "Rajasthan", "Karnataka", "Gujarat", "Andhra Pradesh", "Odisha",
            "Telangana", "Kerala", "Jharkhand", "Assam", "Punjab", "Chhattisgarh",
            "Haryana", "Jammu and Kashmir", "Ladakh", "Uttarakhand", "Himachal Pradesh",
            "Tripura", "Meghalaya", "Manipur", "Nagaland", "Goa", "Arunachal Pradesh",
            "Mizoram", "Sikkim", "Delhi", "Puducherry", "Chandigarh", "Andaman and Nicobar Islands",
            "Dadra and Nagar Haveli and Daman and Diu", "Lakshadweep"
        ]
        
        # Crisis keywords for filtering
        self.crisis_keywords = [
            'flood', 'earthquake', 'cyclone', 'tsunami', 'fire', 'drought', 'landslide',
            'disaster', 'emergency', 'evacuation', 'rescue', 'relief', 'calamity',
            'storm', 'hurricane', 'tornado', 'avalanche', 'blizzard', 'heatwave',
            'coldwave', 'accident', 'explosion', 'collapse', 'leak', 'spill'
        ]
    
    def collect_news_data(self) -> List[Dict[str, Any]]:
        """Collect news data from multiple news APIs"""
        all_news = []
        
        # Collect from NewsAPI
        all_news.extend(self._collect_newsapi_data())
        
        # Collect from MediaStack
        all_news.extend(self._collect_mediastack_data())
        
        # Collect from NewsData.io
        all_news.extend(self._collect_newsdata_data())
        
        return all_news
    
    def _collect_newsapi_data(self) -> List[Dict[str, Any]]:
        """Collect data from NewsAPI"""
        if not self.newsapi_key:
            logger.warning("NewsAPI key not found")
            return []
        
        try:
            news_data = []
            
            # Search for crisis-related news in India
            for keyword in self.crisis_keywords[:5]:  # Limit to avoid API quota
                url = "https://newsapi.org/v2/everything"
                params = {
                    'q': f'{keyword} India',
                    'country': 'in',
                    'language': 'en',
                    'sortBy': 'publishedAt',
                    'from': (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d'),
                    'pageSize': 20,
                    'apiKey': self.newsapi_key
                }
                
                response = requests.get(url, params=params, timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    
                    for article in data.get('articles', []):
                        if self._is_india_related(article.get('title', '') + ' ' + article.get('description', '')):
                            location = self._extract_location(article.get('title', '') + ' ' + article.get('description', ''))
                            coordinates = get_coordinates(location) if location else (20.5937, 78.9629)
                            
                            news_item = {
                                'title': article.get('title', ''),
                                'description': article.get('description', ''),
                                'text': article.get('content', article.get('description', '')),
                                'source': article.get('source', {}).get('name', 'NewsAPI'),
                                'url': article.get('url', ''),
                                'published_at': article.get('publishedAt', ''),
                                'location': location,
                                'latitude': coordinates[0],
                                'longitude': coordinates[1],
                                'api_source': 'newsapi'
                            }
                            news_data.append(news_item)
                
                time.sleep(0.5)  # Rate limiting
            
            logger.info(f"Collected {len(news_data)} articles from NewsAPI")
            return news_data
            
        except Exception as e:
            logger.error(f"Error collecting NewsAPI data: {str(e)}")
            return []
    
    def _collect_mediastack_data(self) -> List[Dict[str, Any]]:
        """Collect data from MediaStack API"""
        if not self.mediastack_key:
            logger.warning("MediaStack key not found")
            return []
        
        try:
            news_data = []
            
            url = "http://api.mediastack.com/v1/news"
            params = {
                'access_key': self.mediastack_key,
                'countries': 'in',
                'languages': 'en',
                'keywords': ','.join(self.crisis_keywords[:10]),
                'limit': 50,
                'date': (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
            }
            
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                for article in data.get('data', []):
                    if self._is_india_related(article.get('title', '') + ' ' + article.get('description', '')):
                        location = self._extract_location(article.get('title', '') + ' ' + article.get('description', ''))
                        coordinates = get_coordinates(location) if location else (20.5937, 78.9629)
                        
                        news_item = {
                            'title': article.get('title', ''),
                            'description': article.get('description', ''),
                            'text': article.get('description', ''),
                            'source': article.get('source', 'MediaStack'),
                            'url': article.get('url', ''),
                            'published_at': article.get('published_at', ''),
                            'location': location,
                            'latitude': coordinates[0],
                            'longitude': coordinates[1],
                            'api_source': 'mediastack'
                        }
                        news_data.append(news_item)
            
            logger.info(f"Collected {len(news_data)} articles from MediaStack")
            return news_data
            
        except Exception as e:
            logger.error(f"Error collecting MediaStack data: {str(e)}")
            return []
    
    def _collect_newsdata_data(self) -> List[Dict[str, Any]]:
        """Collect data from NewsData.io API"""
        if not self.newsdata_key:
            logger.warning("NewsData key not found")
            return []
        
        try:
            news_data = []
            
            url = "https://newsdata.io/api/1/news"
            params = {
                'apikey': self.newsdata_key,
                'country': 'in',
                'language': 'en',
                'q': ' OR '.join(self.crisis_keywords[:10]),
                'size': 50
            }
            
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                for article in data.get('results', []):
                    if self._is_india_related(article.get('title', '') + ' ' + article.get('description', '')):
                        location = self._extract_location(article.get('title', '') + ' ' + article.get('description', ''))
                        coordinates = get_coordinates(location) if location else (20.5937, 78.9629)
                        
                        news_item = {
                            'title': article.get('title', ''),
                            'description': article.get('description', ''),
                            'text': article.get('content', article.get('description', '')),
                            'source': article.get('source_id', 'NewsData'),
                            'url': article.get('link', ''),
                            'published_at': article.get('pubDate', ''),
                            'location': location,
                            'latitude': coordinates[0],
                            'longitude': coordinates[1],
                            'api_source': 'newsdata'
                        }
                        news_data.append(news_item)
            
            logger.info(f"Collected {len(news_data)} articles from NewsData")
            return news_data
            
        except Exception as e:
            logger.error(f"Error collecting NewsData data: {str(e)}")
            return []
    
    def collect_weather_alerts(self) -> List[Dict[str, Any]]:
        """Collect weather alerts from Weatherstack API"""
        if not self.weatherstack_key:
            logger.warning("Weatherstack key not found")
            return []
        
        try:
            weather_alerts = []
            
            # Check weather for major Indian cities
            major_cities = ["Delhi", "Mumbai", "Bangalore", "Chennai", "Kolkata", "Hyderabad"]
            
            for city in major_cities:
                url = "http://api.weatherstack.com/current"
                params = {
                    'access_key': self.weatherstack_key,
                    'query': city,
                    'units': 'm'
                }
                
                response = requests.get(url, params=params, timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    current = data.get('current', {})
                    location = data.get('location', {})
                    
                    # Check for extreme weather conditions
                    temperature = current.get('temperature', 0)
                    weather_desc = current.get('weather_descriptions', [''])[0].lower()
                    wind_speed = current.get('wind_speed', 0)
                    
                    # Define alert conditions
                    if (temperature > 45 or temperature < 0 or wind_speed > 60 or 
                        any(extreme in weather_desc for extreme in ['storm', 'heavy', 'severe', 'extreme'])):
                        
                        alert = {
                            'type': 'weather_alert',
                            'city': location.get('name', city),
                            'country': location.get('country', 'India'),
                            'latitude': location.get('lat', 0),
                            'longitude': location.get('lon', 0),
                            'temperature': temperature,
                            'description': weather_desc,
                            'wind_speed': wind_speed,
                            'timestamp': datetime.now().isoformat(),
                            'severity': self._assess_weather_severity(temperature, wind_speed, weather_desc)
                        }
                        weather_alerts.append(alert)
                
                time.sleep(1)  # Rate limiting
            
            logger.info(f"Collected {len(weather_alerts)} weather alerts")
            return weather_alerts
            
        except Exception as e:
            logger.error(f"Error collecting weather data: {str(e)}")
            return []
    
    def collect_rss_feeds(self) -> List[Dict[str, Any]]:
        """Collect data from RSS feeds"""
        all_rss_data = []
        
        for source_name, feed_url in self.rss_feeds.items():
            try:
                feed = feedparser.parse(feed_url)
                
                for entry in feed.entries[:10]:  # Limit entries per feed
                    # Check if entry is crisis-related
                    title = entry.get('title', '')
                    summary = entry.get('summary', entry.get('description', ''))
                    
                    if self._contains_crisis_keywords(title + ' ' + summary):
                        location = self._extract_location(title + ' ' + summary)
                        coordinates = get_coordinates(location) if location else (20.5937, 78.9629)
                        
                        rss_item = {
                            'title': title,
                            'description': summary,
                            'text': summary,
                            'source': source_name,
                            'url': entry.get('link', ''),
                            'published_at': entry.get('published', entry.get('updated', '')),
                            'location': location,
                            'latitude': coordinates[0],
                            'longitude': coordinates[1],
                            'api_source': 'rss'
                        }
                        all_rss_data.append(rss_item)
                
                time.sleep(0.5)  # Rate limiting
                
            except Exception as e:
                logger.error(f"Error collecting RSS data from {source_name}: {str(e)}")
        
        logger.info(f"Collected {len(all_rss_data)} items from RSS feeds")
        return all_rss_data
    
    def _is_india_related(self, text: str) -> bool:
        """Check if text is related to India"""
        text_lower = text.lower()
        return any(location.lower() in text_lower for location in self.indian_locations)
    
    def _extract_location(self, text: str) -> str:
        """Extract Indian location from text"""
        text_lower = text.lower()
        for location in self.indian_locations:
            if location.lower() in text_lower:
                return location
        return None
    
    def _contains_crisis_keywords(self, text: str) -> bool:
        """Check if text contains crisis-related keywords"""
        text_lower = text.lower()
        return any(keyword in text_lower for keyword in self.crisis_keywords)
    
    def _assess_weather_severity(self, temperature: float, wind_speed: float, description: str) -> str:
        """Assess weather alert severity"""
        if temperature > 50 or temperature < -10 or wind_speed > 100:
            return 'high'
        elif temperature > 45 or temperature < 0 or wind_speed > 60:
            return 'medium'
        else:
            return 'low'
