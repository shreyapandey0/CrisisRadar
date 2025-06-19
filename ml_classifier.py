from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split
import pandas as pd
import numpy as np
import pickle
import os
import re
from typing import Dict, Any, Tuple
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CrisisClassifier:
    def __init__(self):
        """Initialize crisis classifier"""
        self.crisis_model = None
        self.severity_model = None
        self.crisis_types = ['flood', 'earthquake', 'cyclone', 'fire', 'drought', 'landslide', 'storm', 'accident']
        self.severity_levels = ['low', 'medium', 'high']
        
        # Crisis keywords mapping
        self.crisis_keywords = {
            'flood': ['flood', 'flooding', 'inundation', 'waterlogging', 'deluge', 'overflow', 'submersion'],
            'earthquake': ['earthquake', 'quake', 'tremor', 'seismic', 'magnitude', 'epicenter', 'aftershock'],
            'cyclone': ['cyclone', 'hurricane', 'typhoon', 'storm', 'wind', 'gale', 'tempest'],
            'fire': ['fire', 'blaze', 'wildfire', 'burn', 'flame', 'combustion', 'arson'],
            'drought': ['drought', 'dry', 'arid', 'water shortage', 'scarcity', 'parched'],
            'landslide': ['landslide', 'mudslide', 'rockfall', 'slope failure', 'erosion'],
            'storm': ['storm', 'thunderstorm', 'hailstorm', 'lightning', 'thunder'],
            'accident': ['accident', 'crash', 'collision', 'derailment', 'explosion', 'collapse']
        }
        
        # Severity keywords
        self.severity_keywords = {
            'high': ['severe', 'extreme', 'catastrophic', 'devastating', 'massive', 'major', 'critical', 'emergency', 'disaster'],
            'medium': ['moderate', 'significant', 'considerable', 'notable', 'substantial'],
            'low': ['minor', 'small', 'light', 'slight', 'minimal']
        }
        
        # Initialize models
        self._initialize_models()
    
    def _initialize_models(self):
        """Initialize or train ML models"""
        try:
            # Try to load pre-trained models
            if os.path.exists('crisis_model.pkl') and os.path.exists('severity_model.pkl'):
                with open('crisis_model.pkl', 'rb') as f:
                    self.crisis_model = pickle.load(f)
                with open('severity_model.pkl', 'rb') as f:
                    self.severity_model = pickle.load(f)
                logger.info("Loaded pre-trained models")
            else:
                # Train new models with synthetic data
                self._train_models()
                logger.info("Trained new models")
        except Exception as e:
            logger.error(f"Error initializing models: {str(e)}")
            self._train_models()
    
    def _train_models(self):
        """Train crisis classification models with enhanced synthetic data"""
        # Generate training data
        training_data = self._generate_training_data()
        
        # Prepare crisis type classification data
        crisis_texts = []
        crisis_labels = []
        severity_texts = []
        severity_labels = []
        
        for item in training_data:
            crisis_texts.append(item['text'])
            crisis_labels.append(item['crisis_type'])
            severity_texts.append(item['text'])
            severity_labels.append(item['severity'])
        
        # Train crisis type classifier
        self.crisis_model = Pipeline([
            ('tfidf', TfidfVectorizer(max_features=5000, ngram_range=(1, 3), stop_words='english')),
            ('classifier', MultinomialNB(alpha=0.1))
        ])
        
        self.crisis_model.fit(crisis_texts, crisis_labels)
        
        # Train severity classifier
        self.severity_model = Pipeline([
            ('tfidf', TfidfVectorizer(max_features=3000, ngram_range=(1, 2), stop_words='english')),
            ('classifier', MultinomialNB(alpha=0.1))
        ])
        
        self.severity_model.fit(severity_texts, severity_labels)
        
        # Save models
        try:
            with open('crisis_model.pkl', 'wb') as f:
                pickle.dump(self.crisis_model, f)
            with open('severity_model.pkl', 'wb') as f:
                pickle.dump(self.severity_model, f)
            logger.info("Models trained and saved successfully")
        except Exception as e:
            logger.error(f"Error saving models: {str(e)}")
    
    def _generate_training_data(self) -> list:
        """Generate synthetic training data for Indian crisis scenarios"""
        training_data = []
        
        # Flood examples
        flood_examples = [
            ("Heavy monsoon rains cause severe flooding in Mumbai, thousands evacuated", "flood", "high"),
            ("Chennai witnesses waterlogging after overnight rainfall", "flood", "medium"),
            ("Minor flooding reported in low-lying areas of Kolkata", "flood", "low"),
            ("Yamuna river overflows, Delhi on high alert", "flood", "high"),
            ("Assam faces devastating floods, villages submerged", "flood", "high"),
            ("Urban flooding disrupts normal life in Bangalore", "flood", "medium")
        ]
        
        # Earthquake examples
        earthquake_examples = [
            ("Massive 7.2 magnitude earthquake hits northeastern India", "earthquake", "high"),
            ("Tremors felt across Delhi after 5.5 magnitude quake", "earthquake", "medium"),
            ("Minor earthquake of 3.2 magnitude recorded in Himachal Pradesh", "earthquake", "low"),
            ("Strong earthquake jolts Kashmir, buildings evacuated", "earthquake", "high"),
            ("Earthquake of moderate intensity shakes parts of Gujarat", "earthquake", "medium")
        ]
        
        # Cyclone examples
        cyclone_examples = [
            ("Cyclone Yaas makes landfall in Odisha with wind speeds of 140 kmph", "cyclone", "high"),
            ("Severe cyclonic storm approaching Tamil Nadu coast", "cyclone", "high"),
            ("Cyclonic circulation over Bay of Bengal may intensify", "cyclone", "medium"),
            ("West Bengal prepares for impending cyclone", "cyclone", "medium"),
            ("Deep depression in Arabian Sea likely to become cyclone", "cyclone", "low")
        ]
        
        # Fire examples
        fire_examples = [
            ("Massive forest fire engulfs Uttarakhand hills, emergency declared", "fire", "high"),
            ("Industrial fire in Mumbai, several injured", "fire", "medium"),
            ("Minor fire incident at Delhi market, no casualties", "fire", "low"),
            ("Wildfire spreads across Himachal Pradesh forests", "fire", "high"),
            ("Fire breaks out at textile factory in Tamil Nadu", "fire", "medium")
        ]
        
        # Drought examples
        drought_examples = [
            ("Severe drought conditions prevail in Maharashtra, crops fail", "drought", "high"),
            ("Water scarcity hits rural Karnataka", "drought", "medium"),
            ("Minimal rainfall causes drought-like situation in Rajasthan", "drought", "medium"),
            ("Andhra Pradesh faces acute water shortage", "drought", "high"),
            ("Dry spell affects agricultural activities in Punjab", "drought", "low")
        ]
        
        # Landslide examples
        landslide_examples = [
            ("Massive landslide blocks Himachal Pradesh highway", "landslide", "high"),
            ("Heavy rains trigger landslides in Kerala hills", "landslide", "medium"),
            ("Minor landslide reported in Uttarakhand", "landslide", "low"),
            ("Landslide warning issued for mountainous regions", "landslide", "medium"),
            ("Rock fall damages vehicles in hill station", "landslide", "low")
        ]
        
        # Storm examples
        storm_examples = [
            ("Severe thunderstorm with hail hits North India", "storm", "high"),
            ("Lightning strikes claim lives in Bihar", "storm", "high"),
            ("Dust storm engulfs Delhi NCR", "storm", "medium"),
            ("Heavy thunderstorm disrupts flight operations", "storm", "medium"),
            ("Light thunderstorm expected in evening", "storm", "low")
        ]
        
        # Accident examples
        accident_examples = [
            ("Train derailment in UP claims multiple lives", "accident", "high"),
            ("Bus accident on Mumbai-Pune highway", "accident", "medium"),
            ("Industrial accident at chemical plant", "accident", "high"),
            ("Building collapse in construction site", "accident", "medium"),
            ("Minor road accident causes traffic jam", "accident", "low")
        ]
        
        # Combine all examples
        all_examples = (flood_examples + earthquake_examples + cyclone_examples + 
                       fire_examples + drought_examples + landslide_examples + 
                       storm_examples + accident_examples)
        
        for text, crisis_type, severity in all_examples:
            training_data.append({
                'text': text,
                'crisis_type': crisis_type,
                'severity': severity
            })
        
        return training_data
    
    def classify_crisis(self, text: str, location: str = None) -> Dict[str, Any]:
        """Classify if text represents a crisis and determine its type and severity"""
        try:
            # Check if text contains crisis indicators
            is_crisis = self._is_crisis_text(text)
            
            if not is_crisis:
                return {
                    'is_crisis': False,
                    'crisis_type': None,
                    'severity': None,
                    'confidence': 0.0
                }
            
            # Predict crisis type
            if self.crisis_model:
                crisis_proba = self.crisis_model.predict_proba([text])[0]
                crisis_type = self.crisis_model.predict([text])[0]
                crisis_confidence = max(crisis_proba)
            else:
                crisis_type = self._rule_based_crisis_classification(text)
                crisis_confidence = 0.7
            
            # Predict severity
            if self.severity_model:
                severity_proba = self.severity_model.predict_proba([text])[0]
                severity = self.severity_model.predict([text])[0]
                severity_confidence = max(severity_proba)
            else:
                severity = self._rule_based_severity_classification(text)
                severity_confidence = 0.6
            
            # Combine confidences
            overall_confidence = (crisis_confidence + severity_confidence) / 2
            
            return {
                'is_crisis': True,
                'crisis_type': crisis_type,
                'severity': severity,
                'confidence': overall_confidence,
                'location': location
            }
            
        except Exception as e:
            logger.error(f"Error in crisis classification: {str(e)}")
            return {
                'is_crisis': False,
                'crisis_type': None,
                'severity': None,
                'confidence': 0.0
            }
    
    def _is_crisis_text(self, text: str) -> bool:
        """Determine if text represents a crisis using keyword matching"""
        text_lower = text.lower()
        
        # Check for crisis keywords
        crisis_indicators = []
        for crisis_type, keywords in self.crisis_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                crisis_indicators.append(crisis_type)
        
        # Check for general crisis words
        general_crisis_words = ['disaster', 'emergency', 'alert', 'warning', 'evacuate', 'rescue', 'damage', 'casualties', 'injured', 'killed', 'destroyed']
        has_general_crisis = any(word in text_lower for word in general_crisis_words)
        
        return len(crisis_indicators) > 0 or has_general_crisis
    
    def _rule_based_crisis_classification(self, text: str) -> str:
        """Classify crisis type using rule-based approach"""
        text_lower = text.lower()
        
        # Count keyword matches for each crisis type
        type_scores = {}
        for crisis_type, keywords in self.crisis_keywords.items():
            score = sum(1 for keyword in keywords if keyword in text_lower)
            if score > 0:
                type_scores[crisis_type] = score
        
        # Return type with highest score
        if type_scores:
            return max(type_scores.items(), key=lambda x: x[1])[0]
        else:
            return 'accident'  # Default fallback
    
    def _rule_based_severity_classification(self, text: str) -> str:
        """Classify severity using rule-based approach"""
        text_lower = text.lower()
        
        # Check for severity indicators
        for severity, keywords in self.severity_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                return severity
        
        # Check for numbers that might indicate severity
        if re.search(r'\d+\s*(dead|killed|casualties|injured)', text_lower):
            numbers = re.findall(r'\d+', text)
            if numbers:
                max_num = max(int(num) for num in numbers)
                if max_num > 50:
                    return 'high'
                elif max_num > 10:
                    return 'medium'
                else:
                    return 'low'
        
        # Default to medium if no clear indicators
        return 'medium'
    
    def retrain_model(self, new_data: list):
        """Retrain models with new labeled data"""
        try:
            # Combine with existing training data
            existing_data = self._generate_training_data()
            all_data = existing_data + new_data
            
            # Prepare data
            crisis_texts = [item['text'] for item in all_data]
            crisis_labels = [item['crisis_type'] for item in all_data]
            severity_texts = [item['text'] for item in all_data]
            severity_labels = [item['severity'] for item in all_data]
            
            # Retrain models
            self.crisis_model.fit(crisis_texts, crisis_labels)
            self.severity_model.fit(severity_texts, severity_labels)
            
            # Save updated models
            with open('crisis_model.pkl', 'wb') as f:
                pickle.dump(self.crisis_model, f)
            with open('severity_model.pkl', 'wb') as f:
                pickle.dump(self.severity_model, f)
            
            logger.info("Models retrained successfully")
            
        except Exception as e:
            logger.error(f"Error retraining models: {str(e)}")
