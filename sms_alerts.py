import os
from twilio.rest import Client
from typing import List, Dict, Any
import logging
from datetime import datetime, timedelta
from utils import calculate_distance, get_coordinates
import sqlite3

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SMSAlerter:
    def __init__(self):
        """Initialize SMS alerter with Twilio credentials"""
        self.account_sid = os.getenv("TWILIO_ACCOUNT_SID")
        self.auth_token = os.getenv("TWILIO_AUTH_TOKEN")
        self.phone_number = os.getenv("TWILIO_PHONE_NUMBER")
        
        if self.account_sid and self.auth_token:
            self.client = Client(self.account_sid, self.auth_token)
        else:
            logger.warning("Twilio credentials not found")
            self.client = None
        
        # Initialize user database
        self._init_user_database()
        
        # SMS templates for different languages
        self.sms_templates = {
            'English': {
                'crisis_alert': "🚨 CRISIS ALERT: {crisis_type} detected in {location}. Severity: {severity}. Stay safe and follow local authorities' instructions. - CrisisRadar",
                'weather_alert': "🌩️ WEATHER ALERT: {weather_type} in {location}. {description}. Take necessary precautions. - CrisisRadar"
            },
            'Hindi': {
                'crisis_alert': "🚨 संकट चेतावनी: {location} में {crisis_type} का पता चला। गंभीरता: {severity}। सुरक्षित रहें और स्थानीय अधिकारियों के निर्देशों का पालन करें। - CrisisRadar",
                'weather_alert': "🌩️ मौसम चेतावनी: {location} में {weather_type}। {description}। आवश्यक सावधानी बरतें। - CrisisRadar"
            },
            'Bengali': {
                'crisis_alert': "🚨 সংকট সতর্কতা: {location} এ {crisis_type} সনাক্ত হয়েছে। তীব্রতা: {severity}। নিরাপদ থাকুন এবং স্থানীয় কর্তৃপক্ষের নির্দেশাবলী অনুসরণ করুন। - CrisisRadar",
                'weather_alert': "🌩️ আবহাওয়া সতর্কতা: {location} এ {weather_type}। {description}। প্রয়োজনীয় সতর্কতা অবলম্বন করুন। - CrisisRadar"
            },
            'Tamil': {
                'crisis_alert': "🚨 நெருக்கடி எச்சரிக்கை: {location} இல் {crisis_type} கண்டறியப்பட்டது। தீவிரம்: {severity}। பாதுகாப்பாக இருங்கள் மற்றும் உள்ளூர் அதிகாரிகளின் அறிவுரைகளை பின்பற்றுங்கள். - CrisisRadar",
                'weather_alert': "🌩️ வானிலை எச்சரிக்கை: {location} இல் {weather_type}। {description}। தேவையான முன்னெச்சரிக்கை நடவடிக்கைகளை எடுங்கள். - CrisisRadar"
            }
        }
    
    def _init_user_database(self):
        """Initialize SQLite database for user registrations"""
        try:
            conn = sqlite3.connect('sms_users.db')
            cursor = conn.cursor()
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS sms_users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    phone_number TEXT UNIQUE NOT NULL,
                    latitude REAL,
                    longitude REAL,
                    alert_radius INTEGER DEFAULT 50,
                    language TEXT DEFAULT 'English',
                    crisis_types TEXT DEFAULT 'all',
                    registered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    active BOOLEAN DEFAULT TRUE
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS sent_alerts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    phone_number TEXT NOT NULL,
                    alert_type TEXT NOT NULL,
                    crisis_type TEXT,
                    location TEXT,
                    sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    message_sid TEXT
                )
            ''')
            
            conn.commit()
            conn.close()
            logger.info("User database initialized")
            
        except Exception as e:
            logger.error(f"Error initializing user database: {str(e)}")
    
    def register_user(self, phone_number: str, alert_radius: int = 50, location: str = None, 
                     language: str = 'English', crisis_types: List[str] = None) -> bool:
        """Register user for SMS alerts"""
        try:
            # Get coordinates for location
            if location:
                coordinates = get_coordinates(location)
                latitude, longitude = coordinates[0], coordinates[1]
            else:
                latitude, longitude = None, None
            
            # Prepare crisis types
            if crisis_types is None:
                crisis_types_str = 'all'
            else:
                crisis_types_str = ','.join(crisis_types)
            
            # Store in database
            conn = sqlite3.connect('sms_users.db')
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO sms_users 
                (phone_number, latitude, longitude, alert_radius, language, crisis_types)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (phone_number, latitude, longitude, alert_radius, language, crisis_types_str))
            
            conn.commit()
            conn.close()
            
            # Send welcome message
            self._send_welcome_message(phone_number, language)
            
            logger.info(f"User {phone_number} registered for SMS alerts")
            return True
            
        except Exception as e:
            logger.error(f"Error registering user: {str(e)}")
            return False
    
    def send_crisis_alert(self, crisis_data: Dict[str, Any]) -> List[str]:
        """Send crisis alerts to relevant users"""
        if not self.client:
            logger.warning("Twilio client not available")
            return []
        
        try:
            sent_to = []
            
            # Get relevant users
            relevant_users = self._get_relevant_users(crisis_data)
            
            for user in relevant_users:
                phone_number = user['phone_number']
                language = user['language']
                
                # Create personalized message
                message = self._create_crisis_message(crisis_data, language)
                
                # Check if already sent similar alert recently
                if not self._should_send_alert(phone_number, crisis_data):
                    continue
                
                # Send SMS
                try:
                    message_obj = self.client.messages.create(
                        body=message,
                        from_=self.phone_number,
                        to=phone_number
                    )
                    
                    # Log sent alert
                    self._log_sent_alert(phone_number, 'crisis', crisis_data, message_obj.sid)
                    sent_to.append(phone_number)
                    
                    logger.info(f"Crisis alert sent to {phone_number}")
                    
                except Exception as e:
                    logger.error(f"Error sending SMS to {phone_number}: {str(e)}")
            
            return sent_to
            
        except Exception as e:
            logger.error(f"Error sending crisis alerts: {str(e)}")
            return []
    
    def send_weather_alert(self, weather_data: Dict[str, Any]) -> List[str]:
        """Send weather alerts to relevant users"""
        if not self.client:
            logger.warning("Twilio client not available")
            return []
        
        try:
            sent_to = []
            
            # Get relevant users for weather alerts
            relevant_users = self._get_relevant_users_weather(weather_data)
            
            for user in relevant_users:
                phone_number = user['phone_number']
                language = user['language']
                
                # Create weather message
                message = self._create_weather_message(weather_data, language)
                
                # Send SMS
                try:
                    message_obj = self.client.messages.create(
                        body=message,
                        from_=self.phone_number,
                        to=phone_number
                    )
                    
                    # Log sent alert
                    self._log_sent_alert(phone_number, 'weather', weather_data, message_obj.sid)
                    sent_to.append(phone_number)
                    
                    logger.info(f"Weather alert sent to {phone_number}")
                    
                except Exception as e:
                    logger.error(f"Error sending weather SMS to {phone_number}: {str(e)}")
            
            return sent_to
            
        except Exception as e:
            logger.error(f"Error sending weather alerts: {str(e)}")
            return []
    
    def _get_relevant_users(self, crisis_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Get users who should receive this crisis alert"""
        try:
            conn = sqlite3.connect('sms_users.db')
            cursor = conn.cursor()
            
            cursor.execute('SELECT * FROM sms_users WHERE active = TRUE')
            all_users = cursor.fetchall()
            conn.close()
            
            relevant_users = []
            crisis_lat = crisis_data.get('latitude', 20.5937)
            crisis_lon = crisis_data.get('longitude', 78.9629)
            crisis_type = crisis_data.get('crisis_type', '')
            
            for user_row in all_users:
                user = {
                    'phone_number': user_row[1],
                    'latitude': user_row[2],
                    'longitude': user_row[3],
                    'alert_radius': user_row[4],
                    'language': user_row[5],
                    'crisis_types': user_row[6]
                }
                
                # Check if user wants this type of crisis
                if user['crisis_types'] != 'all':
                    user_crisis_types = user['crisis_types'].split(',')
                    if crisis_type not in user_crisis_types:
                        continue
                
                # Check distance
                if user['latitude'] and user['longitude']:
                    distance = calculate_distance(
                        user['latitude'], user['longitude'],
                        crisis_lat, crisis_lon
                    )
                    
                    if distance <= user['alert_radius']:
                        relevant_users.append(user)
                else:
                    # If no location set, send all India alerts
                    relevant_users.append(user)
            
            return relevant_users
            
        except Exception as e:
            logger.error(f"Error getting relevant users: {str(e)}")
            return []
    
    def _get_relevant_users_weather(self, weather_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Get users who should receive weather alerts"""
        try:
            conn = sqlite3.connect('sms_users.db')
            cursor = conn.cursor()
            
            cursor.execute('SELECT * FROM sms_users WHERE active = TRUE')
            all_users = cursor.fetchall()
            conn.close()
            
            relevant_users = []
            weather_lat = weather_data.get('latitude', 20.5937)
            weather_lon = weather_data.get('longitude', 78.9629)
            
            for user_row in all_users:
                user = {
                    'phone_number': user_row[1],
                    'latitude': user_row[2],
                    'longitude': user_row[3],
                    'alert_radius': user_row[4],
                    'language': user_row[5],
                    'crisis_types': user_row[6]
                }
                
                # Check distance for weather alerts (smaller radius)
                if user['latitude'] and user['longitude']:
                    distance = calculate_distance(
                        user['latitude'], user['longitude'],
                        weather_lat, weather_lon
                    )
                    
                    if distance <= min(user['alert_radius'], 100):  # Max 100km for weather
                        relevant_users.append(user)
                else:
                    # Send to all users if no specific location
                    relevant_users.append(user)
            
            return relevant_users
            
        except Exception as e:
            logger.error(f"Error getting relevant users for weather: {str(e)}")
            return []
    
    def _create_crisis_message(self, crisis_data: Dict[str, Any], language: str = 'English') -> str:
        """Create crisis alert message"""
        template = self.sms_templates.get(language, self.sms_templates['English'])['crisis_alert']
        
        return template.format(
            crisis_type=crisis_data.get('crisis_type', 'Unknown').title(),
            location=crisis_data.get('location', 'Unknown'),
            severity=crisis_data.get('severity', 'Unknown').title()
        )
    
    def _create_weather_message(self, weather_data: Dict[str, Any], language: str = 'English') -> str:
        """Create weather alert message"""
        template = self.sms_templates.get(language, self.sms_templates['English'])['weather_alert']
        
        return template.format(
            weather_type=weather_data.get('type', 'Weather Alert'),
            location=weather_data.get('city', 'Unknown'),
            description=weather_data.get('description', 'Check local weather')
        )
    
    def _should_send_alert(self, phone_number: str, crisis_data: Dict[str, Any]) -> bool:
        """Check if we should send alert to avoid spam"""
        try:
            conn = sqlite3.connect('sms_users.db')
            cursor = conn.cursor()
            
            # Check if similar alert sent in last 2 hours
            two_hours_ago = datetime.now() - timedelta(hours=2)
            
            cursor.execute('''
                SELECT COUNT(*) FROM sent_alerts 
                WHERE phone_number = ? AND crisis_type = ? AND location = ? 
                AND sent_at > ?
            ''', (phone_number, crisis_data.get('crisis_type'), 
                  crisis_data.get('location'), two_hours_ago))
            
            count = cursor.fetchone()[0]
            conn.close()
            
            return count == 0
            
        except Exception as e:
            logger.error(f"Error checking alert history: {str(e)}")
            return True  # Send if unsure
    
    def _log_sent_alert(self, phone_number: str, alert_type: str, data: Dict[str, Any], message_sid: str):
        """Log sent alert to database"""
        try:
            conn = sqlite3.connect('sms_users.db')
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO sent_alerts 
                (phone_number, alert_type, crisis_type, location, message_sid)
                VALUES (?, ?, ?, ?, ?)
            ''', (phone_number, alert_type, data.get('crisis_type', data.get('type')), 
                  data.get('location', data.get('city')), message_sid))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Error logging sent alert: {str(e)}")
    
    def _send_welcome_message(self, phone_number: str, language: str = 'English'):
        """Send welcome message to new user"""
        if not self.client:
            return
        
        welcome_messages = {
            'English': "Welcome to CrisisRadar! You'll receive real-time crisis alerts for your area. Reply STOP to unsubscribe.",
            'Hindi': "CrisisRadar में आपका स्वागत है! आपको अपने क्षेत्र के लिए रीयल-टाइम संकट अलर्ट प्राप्त होंगे। सदस्यता रद्द करने के लिए STOP का जवाब दें।",
            'Bengali': "CrisisRadar এ আপনাকে স্বাগতম! আপনি আপনার এলাকার জন্য রিয়েল-টাইম সংকট সতর্কতা পাবেন। সদস্যতা বাতিল করতে STOP উত্তর দিন।",
            'Tamil': "CrisisRadar இல் வரவேற்கிறோம்! உங்கள் பகுதிக்கான நேரடி நெருக்கடி எச்சரிக்கைகளை நீங்கள் பெறுவீர்கள். சந்தாவை ரத்து செய்ய STOP என்று பதிலளிக்கவும்।"
        }
        
        message = welcome_messages.get(language, welcome_messages['English'])
        
        try:
            self.client.messages.create(
                body=message,
                from_=self.phone_number,
                to=phone_number
            )
            logger.info(f"Welcome message sent to {phone_number}")
        except Exception as e:
            logger.error(f"Error sending welcome message: {str(e)}")
    
    def unregister_user(self, phone_number: str) -> bool:
        """Unregister user from SMS alerts"""
        try:
            conn = sqlite3.connect('sms_users.db')
            cursor = conn.cursor()
            
            cursor.execute('UPDATE sms_users SET active = FALSE WHERE phone_number = ?', (phone_number,))
            conn.commit()
            conn.close()
            
            logger.info(f"User {phone_number} unregistered from SMS alerts")
            return True
            
        except Exception as e:
            logger.error(f"Error unregistering user: {str(e)}")
            return False
    
    def get_user_stats(self) -> Dict[str, int]:
        """Get statistics about registered users"""
        try:
            conn = sqlite3.connect('sms_users.db')
            cursor = conn.cursor()
            
            cursor.execute('SELECT COUNT(*) FROM sms_users WHERE active = TRUE')
            active_users = cursor.fetchone()[0]
            
            cursor.execute('SELECT COUNT(*) FROM sent_alerts WHERE DATE(sent_at) = DATE("now")')
            alerts_today = cursor.fetchone()[0]
            
            conn.close()
            
            return {
                'active_users': active_users,
                'alerts_sent_today': alerts_today
            }
            
        except Exception as e:
            logger.error(f"Error getting user stats: {str(e)}")
            return {'active_users': 0, 'alerts_sent_today': 0}
