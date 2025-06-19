import os
import json
import math
from datetime import datetime
from typing import Tuple, Dict, Any
import re
import requests
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def load_config() -> Dict[str, Any]:
    """Load configuration from environment variables"""
    return {
        'newsapi_key': os.getenv('NEWSAPI_KEY'),
        'mediastack_key': os.getenv('MEDIASTACK_KEY'),
        'newsdata_key': os.getenv('NEWSDATA_KEY'),
        'weatherstack_key': os.getenv('WEATHERSTACK_KEY'),
        'twilio_account_sid': os.getenv('TWILIO_ACCOUNT_SID'),
        'twilio_auth_token': os.getenv('TWILIO_AUTH_TOKEN'),
        'twilio_phone_number': os.getenv('TWILIO_PHONE_NUMBER')
    }

def get_coordinates(location: str) -> Tuple[float, float]:
    """Get latitude and longitude for a given location using a simple geocoding approach"""
    if not location:
        return (20.5937, 78.9629)  # Center of India
    
    # Predefined coordinates for major Indian cities and states
    indian_coordinates = {
        # Major Cities
        'mumbai': (19.0760, 72.8777),
        'delhi': (28.6139, 77.2090),
        'bangalore': (12.9716, 77.5946),
        'bengaluru': (12.9716, 77.5946),
        'hyderabad': (17.3850, 78.4867),
        'ahmedabad': (23.0225, 72.5714),
        'chennai': (13.0827, 80.2707),
        'kolkata': (22.5726, 88.3639),
        'surat': (21.1702, 72.8311),
        'pune': (18.5204, 73.8567),
        'jaipur': (26.9124, 75.7873),
        'lucknow': (26.8467, 80.9462),
        'kanpur': (26.4499, 80.3319),
        'nagpur': (21.1458, 79.0882),
        'indore': (22.7196, 75.8577),
        'thane': (19.2183, 72.9781),
        'bhopal': (23.2599, 77.4126),
        'visakhapatnam': (17.6868, 83.2185),
        'patna': (25.5941, 85.1376),
        'vadodara': (22.3072, 73.1812),
        'ghaziabad': (28.6692, 77.4538),
        'ludhiana': (30.9010, 75.8573),
        'agra': (27.1767, 78.0081),
        'nashik': (19.9975, 73.7898),
        'faridabad': (28.4089, 77.3178),
        'meerut': (28.9845, 77.7064),
        'rajkot': (22.3039, 70.8022),
        'varanasi': (25.3176, 82.9739),
        'srinagar': (34.0837, 74.7973),
        'aurangabad': (19.8762, 75.3433),
        'dhanbad': (23.7957, 86.4304),
        'amritsar': (31.6340, 74.8723),
        'allahabad': (25.4358, 81.8463),
        'prayagraj': (25.4358, 81.8463),
        'ranchi': (23.3441, 85.3096),
        'howrah': (22.5958, 88.2636),
        'coimbatore': (11.0168, 76.9558),
        'jabalpur': (23.1815, 79.9864),
        
        # States
        'maharashtra': (19.7515, 75.7139),
        'uttar pradesh': (26.8467, 80.9462),
        'bihar': (25.0961, 85.3131),
        'west bengal': (22.9868, 87.8550),
        'madhya pradesh': (22.9734, 78.6569),
        'tamil nadu': (11.1271, 78.6569),
        'rajasthan': (27.0238, 74.2179),
        'karnataka': (15.3173, 75.7139),
        'gujarat': (22.2587, 71.1924),
        'andhra pradesh': (15.9129, 79.7400),
        'odisha': (20.9517, 85.0985),
        'telangana': (18.1124, 79.0193),
        'kerala': (10.8505, 76.2711),
        'jharkhand': (23.6102, 85.2799),
        'assam': (26.2006, 92.9376),
        'punjab': (31.1471, 75.3412),
        'chhattisgarh': (21.2787, 81.8661),
        'haryana': (29.0588, 76.0856),
        'jammu and kashmir': (34.0837, 74.7973),
        'ladakh': (34.2996, 78.2932),
        'uttarakhand': (30.0668, 79.0193),
        'himachal pradesh': (31.1048, 77.1734),
        'tripura': (23.9408, 91.9882),
        'meghalaya': (25.4670, 91.3662),
        'manipur': (24.6637, 93.9063),
        'nagaland': (26.1584, 94.5624),
        'goa': (15.2993, 74.1240),
        'arunachal pradesh': (28.2180, 94.7278),
        'mizoram': (23.1645, 92.9376),
        'sikkim': (27.5330, 88.5122),
        'puducherry': (11.9416, 79.8083),
        'chandigarh': (30.7333, 76.7794),
        'andaman and nicobar islands': (11.7401, 92.6586),
        'dadra and nagar haveli and daman and diu': (20.3974, 72.8328),
        'lakshadweep': (10.5667, 72.6417),
        
        # Common alternative names
        'bombay': (19.0760, 72.8777),
        'calcutta': (22.5726, 88.3639),
        'madras': (13.0827, 80.2707),
        'mysore': (12.2958, 76.6394),
        'mysuru': (12.2958, 76.6394),
        'mangalore': (12.9141, 74.8560),
        'mangaluru': (12.9141, 74.8560),
        'kochi': (9.9312, 76.2673),
        'cochin': (9.9312, 76.2673),
        'trivandrum': (8.5241, 76.9366),
        'thiruvananthapuram': (8.5241, 76.9366),
        'hubli': (15.3647, 75.1240),
        'hubballi': (15.3647, 75.1240),
        'belgaum': (15.8497, 74.4977),
        'belagavi': (15.8497, 74.4977)
    }
    
    location_lower = location.lower().strip()
    
    # Direct lookup
    if location_lower in indian_coordinates:
        return indian_coordinates[location_lower]
    
    # Partial matching
    for city, coords in indian_coordinates.items():
        if city in location_lower or location_lower in city:
            return coords
    
    # If not found, return center of India
    logger.warning(f"Coordinates not found for location: {location}")
    return (20.5937, 78.9629)

def calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate distance between two points using Haversine formula"""
    # Convert latitude and longitude from degrees to radians
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    
    # Haversine formula
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a))
    
    # Radius of earth in kilometers
    r = 6371
    
    return r * c

def clean_text(text: str) -> str:
    """Clean and normalize text"""
    if not text:
        return ""
    
    # Remove HTML tags
    text = re.sub(r'<[^>]+>', '', text)
    
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text)
    
    # Remove special characters but keep basic punctuation
    text = re.sub(r'[^\w\s\.\,\!\?\-\:\;]', '', text)
    
    return text.strip()

def format_datetime(dt_str: str) -> str:
    """Format datetime string for display"""
    if not dt_str:
        return "Unknown"
    
    try:
        # Try different datetime formats
        formats = [
            '%Y-%m-%dT%H:%M:%SZ',
            '%Y-%m-%dT%H:%M:%S.%fZ',
            '%Y-%m-%d %H:%M:%S',
            '%a, %d %b %Y %H:%M:%S %Z',
            '%a, %d %b %Y %H:%M:%S %z'
        ]
        
        for fmt in formats:
            try:
                dt = datetime.strptime(dt_str, fmt)
                return dt.strftime('%Y-%m-%d %H:%M')
            except ValueError:
                continue
        
        # If all fail, return as is
        return dt_str
        
    except Exception as e:
        logger.error(f"Error formatting datetime {dt_str}: {str(e)}")
        return "Unknown"

def extract_numbers_from_text(text: str) -> list:
    """Extract numbers from text that might indicate casualties or damage"""
    if not text:
        return []
    
    # Find numbers that might indicate severity
    patterns = [
        r'(\d+)\s*(dead|killed|died|deaths?)',
        r'(\d+)\s*(injured|hurt|wounded)',
        r'(\d+)\s*(missing|displaced|evacuated)',
        r'(\d+)\s*(houses?|buildings?|homes?)\s*(destroyed|damaged|collapsed)',
        r'magnitude\s*(\d+\.?\d*)',
        r'(\d+)\s*(kmph|km/h|mph)\s*(wind|speed)',
        r'(\d+)\s*(mm|cm|inches?)\s*(rain|rainfall|precipitation)'
    ]
    
    numbers = []
    text_lower = text.lower()
    
    for pattern in patterns:
        matches = re.findall(pattern, text_lower)
        for match in matches:
            try:
                if isinstance(match, tuple):
                    numbers.append(float(match[0]))
                else:
                    numbers.append(float(match))
            except ValueError:
                continue
    
    return numbers

def validate_phone_number(phone_number: str) -> bool:
    """Validate Indian phone number format"""
    if not phone_number:
        return False
    
    # Remove spaces and special characters
    phone = re.sub(r'[^\d+]', '', phone_number)
    
    # Indian phone number patterns
    patterns = [
        r'^\+91[6-9]\d{9}$',  # +91 followed by 10 digits starting with 6-9
        r'^91[6-9]\d{9}$',    # 91 followed by 10 digits starting with 6-9
        r'^[6-9]\d{9}$'       # 10 digits starting with 6-9
    ]
    
    return any(re.match(pattern, phone) for pattern in patterns)

def normalize_phone_number(phone_number: str) -> str:
    """Normalize phone number to international format"""
    if not phone_number:
        return ""
    
    # Remove all non-digit characters except +
    phone = re.sub(r'[^\d+]', '', phone_number)
    
    # Remove + if present
    phone = phone.lstrip('+')
    
    # Add country code if not present
    if len(phone) == 10 and phone[0] in '6789':
        phone = '91' + phone
    
    # Add + prefix
    return '+' + phone

def get_emergency_contacts() -> Dict[str, str]:
    """Get emergency contact numbers for India"""
    return {
        'Police': '100',
        'Fire': '101',
        'Ambulance': '108',
        'Disaster Management': '1078',
        'Women Helpline': '1091',
        'Child Helpline': '1098',
        'Tourist Helpline': '1363',
        'Railway Accident Emergency': '1072',
        'Road Accident Emergency': '1073',
        'Senior Citizen Helpline': '14567'
    }

def get_crisis_severity_score(text: str, numbers: list = None) -> float:
    """Calculate crisis severity score based on text analysis"""
    if not text:
        return 0.0
    
    text_lower = text.lower()
    score = 0.0
    
    # High severity keywords
    high_severity = ['catastrophic', 'devastating', 'massive', 'severe', 'extreme', 'major', 'critical', 'emergency', 'disaster']
    for keyword in high_severity:
        if keyword in text_lower:
            score += 0.3
    
    # Medium severity keywords
    medium_severity = ['moderate', 'significant', 'considerable', 'notable', 'substantial', 'serious']
    for keyword in medium_severity:
        if keyword in text_lower:
            score += 0.2
    
    # Action keywords that indicate severity
    action_keywords = ['evacuate', 'rescue', 'emergency', 'alert', 'warning', 'declare']
    for keyword in action_keywords:
        if keyword in text_lower:
            score += 0.1
    
    # Number-based severity
    if numbers is None:
        numbers = extract_numbers_from_text(text)
    
    if numbers:
        max_number = max(numbers)
        if max_number > 100:
            score += 0.4
        elif max_number > 50:
            score += 0.3
        elif max_number > 10:
            score += 0.2
        elif max_number > 0:
            score += 0.1
    
    return min(score, 1.0)  # Cap at 1.0

def is_recent_news(published_date: str, hours_threshold: int = 24) -> bool:
    """Check if news is recent (within threshold hours)"""
    if not published_date:
        return False
    
    try:
        # Parse the published date
        dt = datetime.fromisoformat(published_date.replace('Z', '+00:00'))
        now = datetime.now()
        
        # Calculate time difference
        time_diff = now - dt
        
        return time_diff.total_seconds() <= hours_threshold * 3600
        
    except Exception as e:
        logger.error(f"Error checking if news is recent: {str(e)}")
        return False

def sanitize_filename(filename: str) -> str:
    """Sanitize filename for safe file operations"""
    # Remove or replace invalid characters
    sanitized = re.sub(r'[<>:"/\\|?*]', '_', filename)
    
    # Remove leading/trailing spaces and dots
    sanitized = sanitized.strip(' .')
    
    # Limit length
    if len(sanitized) > 255:
        sanitized = sanitized[:255]
    
    return sanitized or 'unnamed_file'
