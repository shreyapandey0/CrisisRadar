import os
from typing import Dict, List, Any, Optional
import logging
from googletrans import Translator
import re
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LanguageProcessor:
    def __init__(self):
        """Initialize language processor with translation capabilities"""
        self.translator = Translator()
        
        # Supported Indian languages
        self.supported_languages = {
            'English': 'en',
            'Hindi': 'hi',
            'Bengali': 'bn',
            'Tamil': 'ta',
            'Telugu': 'te',
            'Marathi': 'mr',
            'Gujarati': 'gu',
            'Kannada': 'kn',
            'Malayalam': 'ml',
            'Odia': 'or',
            'Punjabi': 'pa',
            'Assamese': 'as',
            'Urdu': 'ur',
            'Sanskrit': 'sa'
        }
        
        # Crisis-related terms in different languages
        self.crisis_terms = {
            'en': {
                'flood': ['flood', 'flooding', 'inundation', 'waterlogging', 'deluge'],
                'earthquake': ['earthquake', 'quake', 'tremor', 'seismic'],
                'cyclone': ['cyclone', 'hurricane', 'typhoon', 'storm'],
                'fire': ['fire', 'wildfire', 'blaze', 'burning'],
                'drought': ['drought', 'water scarcity', 'dry spell'],
                'landslide': ['landslide', 'mudslide', 'rockfall'],
                'accident': ['accident', 'crash', 'collision', 'explosion']
            },
            'hi': {
                'flood': ['बाढ़', 'सैलाब', 'जलभराव', 'जल प्रलय'],
                'earthquake': ['भूकंप', 'भूचाल', 'भूकम्प', 'धरती का हिलना'],
                'cyclone': ['चक्रवात', 'तूफान', 'आंधी'],
                'fire': ['आग', 'अग्निकांड', 'दावानल'],
                'drought': ['सूखा', 'अकाल', 'जल संकट'],
                'landslide': ['भूस्खलन', 'पहाड़ी धसकना'],
                'accident': ['दुर्घटना', 'हादसा', 'विस्फोट']
            },
            'bn': {
                'flood': ['বন্যা', 'জলাবদ্ধতা', 'বানভাসি'],
                'earthquake': ['ভূমিকম্প', 'ভূকম্পন', 'কম্পন'],
                'cyclone': ['ঘূর্ণিবায়ু', 'ঝড়', 'সাইক্লোন'],
                'fire': ['অগ্নিকাণ্ড', 'আগুন', 'দাবানল'],
                'drought': ['খরা', 'অনাবৃষ্টি', 'জল সংকট'],
                'landslide': ['ভূমিধস', 'পাহাড় ধস'],
                'accident': ['দুর্ঘটনা', 'হাদিসা', 'বিস্ফোরণ']
            },
            'ta': {
                'flood': ['வெள்ளம்', 'நீர்ப்பெருக்கு', 'நீர் தேக்கம்'],
                'earthquake': ['நிலநடுக்கம்', 'பூகம்பம்', 'அதிர்வு'],
                'cyclone': ['சூறாவளி', 'புயல்', 'காற்றுச்சுழி'],
                'fire': ['தீ', 'தீயணைப்பு', 'காட்டுத்தீ'],
                'drought': ['வறட்சி', 'நீர்ப்பற்றாக்குறை'],
                'landslide': ['மலையடிவு', 'நிலச்சரிவு'],
                'accident': ['விபத்து', 'கீழுள்ளே', 'வெடிப்பு']
            },
            'te': {
                'flood': ['వరదలు', 'నీటి ప్రవాహం', 'జలప్రళయం'],
                'earthquake': ['భూకంపం', 'భూమి వణుకు', 'కంపనలు'],
                'cyclone': ['తుఫాను', 'సైక్లోన్', 'గాలివాన'],
                'fire': ['అగ్నిప్రమాదం', 'మంట', 'కావునల'],
                'drought': ['కరువు', 'నీటి కొరత', 'వర్షాలు లేకపోవడం'],
                'landslide': ['కొండ చరియలు', 'మట్టి కొట్టుకుపోవడం'],
                'accident': ['ప్రమాదం', 'దురాక్రమణ', 'పేలుడు']
            }
        }
        
        # Initialize translation cache to avoid repeated API calls
        self.translation_cache = {}
    
    def detect_language(self, text: str) -> str:
        """Detect the language of given text"""
        try:
            if not text or not text.strip():
                return 'en'
            
            detection = self.translator.detect(text)
            detected_lang = detection.lang
            
            # Map detected language to our supported languages
            for lang_name, lang_code in self.supported_languages.items():
                if lang_code == detected_lang:
                    return lang_name
            
            return 'English'  # Default fallback
            
        except Exception as e:
            logger.error(f"Error detecting language: {str(e)}")
            return 'English'
    
    def translate_text(self, text: str, target_language: str) -> str:
        """Translate text to target language"""
        try:
            if not text or not text.strip():
                return text
            
            # Check if target language is supported
            if target_language not in self.supported_languages:
                logger.warning(f"Unsupported language: {target_language}")
                return text
            
            # If already in English and target is English, return as is
            if target_language == 'English':
                return text
            
            # Check cache first
            cache_key = f"{text}_{target_language}"
            if cache_key in self.translation_cache:
                return self.translation_cache[cache_key]
            
            # Get target language code
            target_code = self.supported_languages[target_language]
            
            # Perform translation
            translation = self.translator.translate(text, dest=target_code)
            translated_text = translation.text
            
            # Cache the translation
            self.translation_cache[cache_key] = translated_text
            
            return translated_text
            
        except Exception as e:
            logger.error(f"Error translating text: {str(e)}")
            return text  # Return original text if translation fails
    
    def translate_crisis_data(self, crisis_data: Dict[str, Any], target_language: str) -> Dict[str, Any]:
        """Translate crisis data to target language"""
        try:
            if target_language == 'English':
                return crisis_data
            
            translated_data = crisis_data.copy()
            
            # Translate title
            if 'title' in translated_data:
                translated_data['title'] = self.translate_text(translated_data['title'], target_language)
            
            # Translate description
            if 'description' in translated_data:
                translated_data['description'] = self.translate_text(translated_data['description'], target_language)
            
            # Translate crisis type
            if 'crisis_type' in translated_data:
                crisis_type_translated = self.translate_crisis_type(translated_data['crisis_type'], target_language)
                translated_data['crisis_type_translated'] = crisis_type_translated
            
            return translated_data
            
        except Exception as e:
            logger.error(f"Error translating crisis data: {str(e)}")
            return crisis_data
    
    def translate_crisis_type(self, crisis_type: str, target_language: str) -> str:
        """Translate crisis type to target language"""
        crisis_translations = {
            'English': {
                'flood': 'Flood',
                'earthquake': 'Earthquake', 
                'cyclone': 'Cyclone',
                'fire': 'Fire',
                'drought': 'Drought',
                'landslide': 'Landslide',
                'accident': 'Accident',
                'storm': 'Storm'
            },
            'Hindi': {
                'flood': 'बाढ़',
                'earthquake': 'भूकंप',
                'cyclone': 'चक्रवात',
                'fire': 'आग',
                'drought': 'सूखा',
                'landslide': 'भूस्खलन',
                'accident': 'दुर्घटना',
                'storm': 'तूफान'
            },
            'Bengali': {
                'flood': 'বন্যা',
                'earthquake': 'ভূমিকম্প',
                'cyclone': 'ঘূর্ণিবায়ু',
                'fire': 'অগ্নিকাণ্ড',
                'drought': 'খরা',
                'landslide': 'ভূমিধস',
                'accident': 'দুর্ঘটনা',
                'storm': 'ঝড়'
            },
            'Tamil': {
                'flood': 'வெள்ளம்',
                'earthquake': 'நிலநடுக்கம்',
                'cyclone': 'சூறாவளி',
                'fire': 'தீ',
                'drought': 'வறட்சி',
                'landslide': 'மலையடிவு',
                'accident': 'விபத்து',
                'storm': 'புயல்'
            },
            'Telugu': {
                'flood': 'వరదలు',
                'earthquake': 'భూకంపం',
                'cyclone': 'తుఫాను',
                'fire': 'అగ్నిప్రమాదం',
                'drought': 'కరువు',
                'landslide': 'కొండ చరియలు',
                'accident': 'ప్రమాదం',
                'storm': 'తుఫాను'
            }
        }
        
        translations = crisis_translations.get(target_language, {})
        return translations.get(crisis_type.lower(), crisis_type.title())
    
    def detect_crisis_in_regional_text(self, text: str, language: str = None) -> Dict[str, Any]:
        """Detect crisis-related content in regional language text"""
        try:
            if not text:
                return {'is_crisis': False, 'crisis_types': [], 'confidence': 0.0}
            
            # Detect language if not provided
            if not language:
                language = self.detect_language(text)
            
            # Get language code
            lang_code = self.supported_languages.get(language, 'en')
            
            text_lower = text.lower()
            detected_crises = []
            
            # Check for crisis terms in the detected language
            crisis_terms = self.crisis_terms.get(lang_code, self.crisis_terms['en'])
            
            for crisis_type, terms in crisis_terms.items():
                for term in terms:
                    if term.lower() in text_lower:
                        detected_crises.append(crisis_type)
                        break
            
            # Remove duplicates
            detected_crises = list(set(detected_crises))
            
            # Calculate confidence based on number of matches
            confidence = min(len(detected_crises) * 0.3, 1.0)
            
            return {
                'is_crisis': len(detected_crises) > 0,
                'crisis_types': detected_crises,
                'confidence': confidence,
                'detected_language': language
            }
            
        except Exception as e:
            logger.error(f"Error detecting crisis in regional text: {str(e)}")
            return {'is_crisis': False, 'crisis_types': [], 'confidence': 0.0}
    
    def get_multilingual_alert_template(self, language: str, alert_type: str = 'crisis') -> str:
        """Get SMS alert template in specified language"""
        templates = {
            'English': {
                'crisis': "🚨 CRISIS ALERT: {crisis_type} detected in {location}. Severity: {severity}. Stay safe and follow local authorities' instructions. - CrisisRadar",
                'weather': "🌩️ WEATHER ALERT: {weather_type} in {location}. {description}. Take necessary precautions. - CrisisRadar"
            },
            'Hindi': {
                'crisis': "🚨 संकट चेतावनी: {location} में {crisis_type} का पता चला। गंभीरता: {severity}। सुरक्षित रहें और स्थानीय अधिकारियों के निर्देशों का पालन करें। - CrisisRadar",
                'weather': "🌩️ मौसम चेतावनी: {location} में {weather_type}। {description}। आवश्यक सावधानी बरतें। - CrisisRadar"
            },
            'Bengali': {
                'crisis': "🚨 সংকট সতর্কতা: {location} এ {crisis_type} সনাক্ত হয়েছে। তীব্রতা: {severity}। নিরাপদ থাকুন এবং স্থানীয় কর্তৃপক্ষের নির্দেশাবলী অনুসরণ করুন। - CrisisRadar",
                'weather': "🌩️ আবহাওয়া সতর্কতা: {location} এ {weather_type}। {description}। প্রয়োজনীয় সতর্কতা অবলম্বন করুন। - CrisisRadar"
            },
            'Tamil': {
                'crisis': "🚨 நெருக்கடி எச்சரிக்கை: {location} இல் {crisis_type} கண்டறியப்பட்டது। தீவிரம்: {severity}। பாதுகாப்பாக இருங்கள் மற்றும் உள்ளூர் அதிகாரிகளின் அறிவுரைகளை பின்பற்றுங்கள். - CrisisRadar",
                'weather': "🌩️ வானிலை எச்சரிக்கை: {location} இல் {weather_type}। {description}। தேவையான முன்னெச்சரிக்கை நடவடிக்கைகளை எடுங்கள். - CrisisRadar"
            },
            'Telugu': {
                'crisis': "🚨 సంక్షోభ హెచ్చరిక: {location} లో {crisis_type} గుర్తించబడింది। తీవ్రత: {severity}। సురక్షితంగా ఉండండి మరియు స్థానిక అధికారుల సూచనలను అనుసరించండి। - CrisisRadar",
                'weather': "🌩️ వాతావరణ హెచ్చరిక: {location} లో {weather_type}। {description}। అవసరమైన జాగ్రత్తలు తీసుకోండి। - CrisisRadar"
            }
        }
        
        return templates.get(language, templates['English']).get(alert_type, templates['English']['crisis'])
    
    def process_multilingual_rss(self, rss_content: str) -> Dict[str, Any]:
        """Process RSS content that may be in regional languages"""
        try:
            # Detect language
            detected_language = self.detect_language(rss_content)
            
            # Check for crisis content in regional language
            crisis_detection = self.detect_crisis_in_regional_text(rss_content, detected_language)
            
            # Translate to English for further processing if needed
            english_content = rss_content
            if detected_language != 'English':
                english_content = self.translate_text(rss_content, 'English')
            
            return {
                'original_content': rss_content,
                'english_content': english_content,
                'detected_language': detected_language,
                'crisis_detection': crisis_detection
            }
            
        except Exception as e:
            logger.error(f"Error processing multilingual RSS: {str(e)}")
            return {
                'original_content': rss_content,
                'english_content': rss_content,
                'detected_language': 'English',
                'crisis_detection': {'is_crisis': False, 'crisis_types': [], 'confidence': 0.0}
            }
    
    def get_supported_languages(self) -> List[str]:
        """Get list of supported languages"""
        return list(self.supported_languages.keys())
    
    def get_language_code(self, language_name: str) -> str:
        """Get language code for language name"""
        return self.supported_languages.get(language_name, 'en')
    
    def clean_regional_text(self, text: str) -> str:
        """Clean and normalize regional language text"""
        if not text:
            return ""
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove special characters but preserve regional language characters
        # Keep Devanagari, Bengali, Tamil, Telugu, etc. Unicode ranges
        text = re.sub(r'[^\w\s\u0900-\u097F\u0980-\u09FF\u0B80-\u0BFF\u0C00-\u0C7F\u0A80-\u0AFF\u0D00-\u0D7F\.\,\!\?\-\:\;]', '', text)
        
        return text.strip()
    
    def get_emergency_phrases(self, language: str) -> Dict[str, str]:
        """Get common emergency phrases in specified language"""
        phrases = {
            'English': {
                'help': 'Help',
                'emergency': 'Emergency',
                'evacuate': 'Evacuate',
                'safe': 'Safe',
                'danger': 'Danger',
                'call_police': 'Call Police',
                'call_ambulance': 'Call Ambulance'
            },
            'Hindi': {
                'help': 'मदद',
                'emergency': 'आपातकाल',
                'evacuate': 'निकासी',
                'safe': 'सुरक्षित',
                'danger': 'खतरा',
                'call_police': 'पुलिस को फोन करें',
                'call_ambulance': 'एम्बुलेंस को फोन करें'
            },
            'Bengali': {
                'help': 'সাহায্য',
                'emergency': 'জরুরী অবস্থা',
                'evacuate': 'সরিয়ে নেওয়া',
                'safe': 'নিরাপদ',
                'danger': 'বিপদ',
                'call_police': 'পুলিশকে ফোন করুন',
                'call_ambulance': 'অ্যাম্বুলেন্সকে ফোন করুন'
            },
            'Tamil': {
                'help': 'உதவி',
                'emergency': 'அவசரநிலை',
                'evacuate': 'வெளியேற்று',
                'safe': 'பாதுகாப்பான',
                'danger': 'ஆபத்து',
                'call_police': 'காவல்துறையை அழைக்கவும்',
                'call_ambulance': 'ஆம்புலன்ஸை அழைக்கவும்'
            },
            'Telugu': {
                'help': 'సహాయం',
                'emergency': 'అత్యవసర పరిస్థితి',
                'evacuate': 'ఖాళీ చేయండి',
                'safe': 'సురక్షితమైన',
                'danger': 'ప్రమాదం',
                'call_police': 'పోలీసులను పిలవండి',
                'call_ambulance': 'అంబులెన్స్ పిలవండి'
            }
        }
        
        return phrases.get(language, phrases['English'])

