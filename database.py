import sqlite3
import json
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
import logging
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CrisisDatabase:
    def __init__(self, db_path: str = 'crisis_data.db'):
        """Initialize crisis database"""
        self.db_path = db_path
        self._initialize_database()
    
    def _initialize_database(self):
        """Create database tables if they don't exist"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Crisis data table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS crisis_data (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    description TEXT,
                    crisis_type TEXT NOT NULL,
                    severity TEXT NOT NULL,
                    location TEXT,
                    latitude REAL,
                    longitude REAL,
                    source TEXT,
                    url TEXT,
                    published_at TEXT,
                    detected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    confidence REAL DEFAULT 0.0,
                    api_source TEXT,
                    is_verified BOOLEAN DEFAULT FALSE,
                    status TEXT DEFAULT 'active'
                )
            ''')
            
            # Weather alerts table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS weather_alerts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    alert_type TEXT NOT NULL,
                    city TEXT NOT NULL,
                    country TEXT DEFAULT 'India',
                    latitude REAL,
                    longitude REAL,
                    temperature REAL,
                    description TEXT,
                    wind_speed REAL,
                    severity TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    is_active BOOLEAN DEFAULT TRUE
                )
            ''')
            
            # User locations for targeted alerts
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS user_locations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT NOT NULL,
                    location_name TEXT NOT NULL,
                    latitude REAL NOT NULL,
                    longitude REAL NOT NULL,
                    alert_radius INTEGER DEFAULT 50,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    is_active BOOLEAN DEFAULT TRUE
                )
            ''')
            
            # Crisis statistics table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS crisis_statistics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date DATE NOT NULL,
                    crisis_type TEXT NOT NULL,
                    location TEXT,
                    count INTEGER DEFAULT 1,
                    severity_high INTEGER DEFAULT 0,
                    severity_medium INTEGER DEFAULT 0,
                    severity_low INTEGER DEFAULT 0,
                    UNIQUE(date, crisis_type, location)
                )
            ''')
            
            # RSS feed tracking
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS rss_tracking (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    feed_name TEXT NOT NULL,
                    feed_url TEXT NOT NULL,
                    last_checked TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_successful TIMESTAMP,
                    items_processed INTEGER DEFAULT 0,
                    error_count INTEGER DEFAULT 0,
                    is_active BOOLEAN DEFAULT TRUE
                )
            ''')
            
            # API usage tracking
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS api_usage (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    api_name TEXT NOT NULL,
                    endpoint TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    status_code INTEGER,
                    response_time REAL,
                    items_returned INTEGER DEFAULT 0,
                    error_message TEXT
                )
            ''')
            
            # Historical trends
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS historical_trends (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    period_start DATE NOT NULL,
                    period_end DATE NOT NULL,
                    location TEXT NOT NULL,
                    crisis_type TEXT NOT NULL,
                    total_incidents INTEGER DEFAULT 0,
                    avg_severity REAL DEFAULT 0.0,
                    trend_direction TEXT,
                    confidence_score REAL DEFAULT 0.0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Create indexes for better performance
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_crisis_type ON crisis_data(crisis_type)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_crisis_location ON crisis_data(location)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_crisis_severity ON crisis_data(severity)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_crisis_date ON crisis_data(detected_at)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_weather_city ON weather_alerts(city)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_weather_date ON weather_alerts(timestamp)')
            
            conn.commit()
            conn.close()
            
            logger.info("Database initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing database: {str(e)}")
    
    def store_crisis_data(self, crisis_items: List[Dict[str, Any]]) -> int:
        """Store crisis data in database"""
        try:
            if not crisis_items:
                return 0
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            stored_count = 0
            
            for item in crisis_items:
                # Check if similar item already exists (avoid duplicates)
                cursor.execute('''
                    SELECT id FROM crisis_data 
                    WHERE title = ? AND location = ? AND crisis_type = ?
                    AND DATE(detected_at) = DATE('now')
                ''', (item.get('title', ''), item.get('location', ''), item.get('crisis_type', '')))
                
                if cursor.fetchone() is None:
                    # Insert new crisis data
                    cursor.execute('''
                        INSERT INTO crisis_data 
                        (title, description, crisis_type, severity, location, latitude, longitude, 
                         source, url, published_at, confidence, api_source)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        item.get('title', ''),
                        item.get('description', ''),
                        item.get('crisis_type', 'unknown'),
                        item.get('severity', 'medium'),
                        item.get('location', ''),
                        item.get('latitude', 0.0),
                        item.get('longitude', 0.0),
                        item.get('source', ''),
                        item.get('url', ''),
                        item.get('published_at', ''),
                        item.get('confidence', 0.0),
                        item.get('api_source', '')
                    ))
                    stored_count += 1
                    
                    # Update statistics
                    self._update_crisis_statistics(item)
            
            conn.commit()
            conn.close()
            
            logger.info(f"Stored {stored_count} new crisis items in database")
            return stored_count
            
        except Exception as e:
            logger.error(f"Error storing crisis data: {str(e)}")
            return 0
    
    def store_weather_data(self, weather_items: List[Dict[str, Any]]) -> int:
        """Store weather alert data in database"""
        try:
            if not weather_items:
                return 0
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            stored_count = 0
            
            for item in weather_items:
                # Check if similar weather alert already exists
                cursor.execute('''
                    SELECT id FROM weather_alerts 
                    WHERE city = ? AND alert_type = ?
                    AND DATE(timestamp) = DATE('now')
                ''', (item.get('city', ''), item.get('type', '')))
                
                if cursor.fetchone() is None:
                    cursor.execute('''
                        INSERT INTO weather_alerts 
                        (alert_type, city, country, latitude, longitude, temperature, 
                         description, wind_speed, severity)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        item.get('type', 'weather_alert'),
                        item.get('city', ''),
                        item.get('country', 'India'),
                        item.get('latitude', 0.0),
                        item.get('longitude', 0.0),
                        item.get('temperature', 0.0),
                        item.get('description', ''),
                        item.get('wind_speed', 0.0),
                        item.get('severity', 'medium')
                    ))
                    stored_count += 1
            
            conn.commit()
            conn.close()
            
            logger.info(f"Stored {stored_count} new weather alerts in database")
            return stored_count
            
        except Exception as e:
            logger.error(f"Error storing weather data: {str(e)}")
            return 0
    
    def get_recent_crises(self, hours: int = 24, limit: int = 100) -> List[Dict[str, Any]]:
        """Get recent crisis data"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT * FROM crisis_data 
                WHERE detected_at >= datetime('now', '-{} hours')
                ORDER BY detected_at DESC 
                LIMIT ?
            '''.format(hours), (limit,))
            
            rows = cursor.fetchall()
            conn.close()
            
            # Convert to list of dictionaries
            columns = ['id', 'title', 'description', 'crisis_type', 'severity', 'location', 
                      'latitude', 'longitude', 'source', 'url', 'published_at', 'detected_at',
                      'confidence', 'api_source', 'is_verified', 'status']
            
            crises = []
            for row in rows:
                crisis = dict(zip(columns, row))
                crises.append(crisis)
            
            return crises
            
        except Exception as e:
            logger.error(f"Error getting recent crises: {str(e)}")
            return []
    
    def get_crisis_by_location(self, location: str, radius_km: float = 50) -> List[Dict[str, Any]]:
        """Get crises near a specific location"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # For simplicity, using location string matching
            # In production, would use geographic distance calculations
            cursor.execute('''
                SELECT * FROM crisis_data 
                WHERE location LIKE ? 
                AND detected_at >= datetime('now', '-7 days')
                ORDER BY detected_at DESC
            ''', (f'%{location}%',))
            
            rows = cursor.fetchall()
            conn.close()
            
            columns = ['id', 'title', 'description', 'crisis_type', 'severity', 'location', 
                      'latitude', 'longitude', 'source', 'url', 'published_at', 'detected_at',
                      'confidence', 'api_source', 'is_verified', 'status']
            
            crises = []
            for row in rows:
                crisis = dict(zip(columns, row))
                crises.append(crisis)
            
            return crises
            
        except Exception as e:
            logger.error(f"Error getting crises by location: {str(e)}")
            return []
    
    def get_crisis_statistics(self, days: int = 30) -> Dict[str, Any]:
        """Get crisis statistics for specified period"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Total crises by type
            cursor.execute('''
                SELECT crisis_type, COUNT(*) as count 
                FROM crisis_data 
                WHERE detected_at >= datetime('now', '-{} days')
                GROUP BY crisis_type
                ORDER BY count DESC
            '''.format(days))
            
            crisis_types = dict(cursor.fetchall())
            
            # Total crises by severity
            cursor.execute('''
                SELECT severity, COUNT(*) as count 
                FROM crisis_data 
                WHERE detected_at >= datetime('now', '-{} days')
                GROUP BY severity
            '''.format(days))
            
            severity_counts = dict(cursor.fetchall())
            
            # Top affected locations
            cursor.execute('''
                SELECT location, COUNT(*) as count 
                FROM crisis_data 
                WHERE detected_at >= datetime('now', '-{} days')
                AND location IS NOT NULL AND location != ''
                GROUP BY location
                ORDER BY count DESC
                LIMIT 10
            '''.format(days))
            
            top_locations = dict(cursor.fetchall())
            
            # Daily trends
            cursor.execute('''
                SELECT DATE(detected_at) as date, COUNT(*) as count 
                FROM crisis_data 
                WHERE detected_at >= datetime('now', '-{} days')
                GROUP BY DATE(detected_at)
                ORDER BY date
            '''.format(days))
            
            daily_trends = dict(cursor.fetchall())
            
            # Total counts
            cursor.execute('''
                SELECT COUNT(*) FROM crisis_data 
                WHERE detected_at >= datetime('now', '-{} days')
            '''.format(days))
            
            total_crises = cursor.fetchone()[0]
            
            conn.close()
            
            return {
                'total_crises': total_crises,
                'crisis_types': crisis_types,
                'severity_counts': severity_counts,
                'top_locations': top_locations,
                'daily_trends': daily_trends,
                'period_days': days
            }
            
        except Exception as e:
            logger.error(f"Error getting crisis statistics: {str(e)}")
            return {}
    
    def _update_crisis_statistics(self, crisis_item: Dict[str, Any]):
        """Update crisis statistics table"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            today = datetime.now().date()
            crisis_type = crisis_item.get('crisis_type', 'unknown')
            location = crisis_item.get('location', 'unknown')
            severity = crisis_item.get('severity', 'medium')
            
            # Check if record exists for today
            cursor.execute('''
                SELECT id FROM crisis_statistics 
                WHERE date = ? AND crisis_type = ? AND location = ?
            ''', (today, crisis_type, location))
            
            if cursor.fetchone():
                # Update existing record
                severity_col = f'severity_{severity}' if severity in ['high', 'medium', 'low'] else 'severity_medium'
                cursor.execute(f'''
                    UPDATE crisis_statistics 
                    SET count = count + 1, {severity_col} = {severity_col} + 1
                    WHERE date = ? AND crisis_type = ? AND location = ?
                ''', (today, crisis_type, location))
            else:
                # Insert new record
                high_count = 1 if severity == 'high' else 0
                medium_count = 1 if severity == 'medium' else 0
                low_count = 1 if severity == 'low' else 0
                
                cursor.execute('''
                    INSERT INTO crisis_statistics 
                    (date, crisis_type, location, count, severity_high, severity_medium, severity_low)
                    VALUES (?, ?, ?, 1, ?, ?, ?)
                ''', (today, crisis_type, location, high_count, medium_count, low_count))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Error updating crisis statistics: {str(e)}")
    
    def log_api_usage(self, api_name: str, endpoint: str = None, status_code: int = None, 
                     response_time: float = None, items_returned: int = 0, error_message: str = None):
        """Log API usage for monitoring and rate limiting"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO api_usage 
                (api_name, endpoint, status_code, response_time, items_returned, error_message)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (api_name, endpoint, status_code, response_time, items_returned, error_message))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Error logging API usage: {str(e)}")
    
    def get_api_usage_stats(self, hours: int = 24) -> Dict[str, Any]:
        """Get API usage statistics"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT api_name, COUNT(*) as calls, 
                       AVG(response_time) as avg_response_time,
                       SUM(items_returned) as total_items,
                       COUNT(CASE WHEN status_code >= 400 THEN 1 END) as errors
                FROM api_usage 
                WHERE timestamp >= datetime('now', '-{} hours')
                GROUP BY api_name
            '''.format(hours))
            
            stats = {}
            for row in cursor.fetchall():
                api_name, calls, avg_response_time, total_items, errors = row
                stats[api_name] = {
                    'calls': calls,
                    'avg_response_time': round(avg_response_time or 0, 2),
                    'total_items': total_items or 0,
                    'errors': errors or 0,
                    'success_rate': round(((calls - (errors or 0)) / calls * 100) if calls > 0 else 0, 2)
                }
            
            conn.close()
            return stats
            
        except Exception as e:
            logger.error(f"Error getting API usage stats: {str(e)}")
            return {}
    
    def cleanup_old_data(self, days_to_keep: int = 30):
        """Clean up old data to manage database size"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Remove old crisis data
            cursor.execute('''
                DELETE FROM crisis_data 
                WHERE detected_at < datetime('now', '-{} days')
            '''.format(days_to_keep))
            
            crisis_deleted = cursor.rowcount
            
            # Remove old weather alerts
            cursor.execute('''
                DELETE FROM weather_alerts 
                WHERE timestamp < datetime('now', '-{} days')
            '''.format(days_to_keep))
            
            weather_deleted = cursor.rowcount
            
            # Remove old API usage logs
            cursor.execute('''
                DELETE FROM api_usage 
                WHERE timestamp < datetime('now', '-{} days')
            '''.format(days_to_keep))
            
            api_deleted = cursor.rowcount
            
            conn.commit()
            conn.close()
            
            logger.info(f"Cleanup completed: {crisis_deleted} crisis records, {weather_deleted} weather records, {api_deleted} API logs deleted")
            
        except Exception as e:
            logger.error(f"Error during cleanup: {str(e)}")
    
    def get_database_info(self) -> Dict[str, Any]:
        """Get database information and statistics"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get table counts
            tables = ['crisis_data', 'weather_alerts', 'user_locations', 'crisis_statistics', 'api_usage']
            table_counts = {}
            
            for table in tables:
                cursor.execute(f'SELECT COUNT(*) FROM {table}')
                table_counts[table] = cursor.fetchone()[0]
            
            # Get database size
            cursor.execute("SELECT page_count * page_size as size FROM pragma_page_count(), pragma_page_size()")
            db_size = cursor.fetchone()[0]
            
            conn.close()
            
            return {
                'database_path': self.db_path,
                'database_size_bytes': db_size,
                'database_size_mb': round(db_size / (1024 * 1024), 2),
                'table_counts': table_counts,
                'total_records': sum(table_counts.values())
            }
            
        except Exception as e:
            logger.error(f"Error getting database info: {str(e)}")
            return {}
    
    def search_crises(self, query: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Search crises by text query"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT * FROM crisis_data 
                WHERE (title LIKE ? OR description LIKE ? OR location LIKE ?)
                AND detected_at >= datetime('now', '-30 days')
                ORDER BY detected_at DESC 
                LIMIT ?
            ''', (f'%{query}%', f'%{query}%', f'%{query}%', limit))
            
            rows = cursor.fetchall()
            conn.close()
            
            columns = ['id', 'title', 'description', 'crisis_type', 'severity', 'location', 
                      'latitude', 'longitude', 'source', 'url', 'published_at', 'detected_at',
                      'confidence', 'api_source', 'is_verified', 'status']
            
            results = []
            for row in rows:
                crisis = dict(zip(columns, row))
                results.append(crisis)
            
            return results
            
        except Exception as e:
            logger.error(f"Error searching crises: {str(e)}")
            return []

