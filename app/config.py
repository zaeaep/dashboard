"""
Configuration management for the Personal Dashboard application.
All configuration values are centralized here.
"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Config:
    """Base configuration class"""
    
    # Flask Settings
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'
    HOST = os.getenv('HOST', '0.0.0.0')
    PORT = int(os.getenv('PORT', 5000))
    
    # API Keys
    OPEN_WEB_UI_API_KEY = os.getenv('OPEN_WEB_UI_API_KEY')
    WEATHER_API_KEY = os.getenv('WEATHER_API_KEY')
    GARMIN_EMAIL = os.getenv('GARMIN_EMAIL')
    GARMIN_PASSWORD = os.getenv('GARMIN_PASSWORD')
    
    # API Endpoints
    OPEN_WEB_UI_BASE_URL = os.getenv('OPEN_WEB_UI_BASE_URL', 'https://openwebui.uni-freiburg.de')
    OPEN_WEB_UI_CHAT_ENDPOINT = '/api/v1/chat/completions'
    OPEN_WEB_UI_MODEL = os.getenv('OPEN_WEB_UI_MODEL', 'openai/gpt-5.2-llmlb')
    
    # OpenWeatherMap Settings
    WEATHER_CITY = os.getenv('WEATHER_CITY', 'Freiburg')
    WEATHER_API_URL = 'http://api.openweathermap.org/data/2.5/weather'
    
    # Google Calendar Settings
    GOOGLE_CALENDAR_SCOPES = [
        'https://www.googleapis.com/auth/calendar.readonly',
        'https://www.googleapis.com/auth/calendar.events'
    ]
    CREDENTIALS_FILE = os.getenv('CREDENTIALS_FILE', 'credentials.json')
    TOKEN_FILE = os.getenv('TOKEN_FILE', 'token.pickle')
    
    # Calendar Filter
    # Leave empty list to include all calendars
    # Or specify calendar names/IDs: ['Work', 'Personal', 'email@gmail.com']
    CALENDAR_FILTER = os.getenv('CALENDAR_FILTER', '').split(',') if os.getenv('CALENDAR_FILTER') else []
    
    # Date/Time Settings
    TIMEZONE = os.getenv('TIMEZONE', 'Europe/Berlin')  # MEZ/CEST
    CALENDAR_MONTHS_AHEAD = int(os.getenv('CALENDAR_MONTHS_AHEAD', 2))
    
    # AI Settings
    AI_REQUEST_TIMEOUT = int(os.getenv('AI_REQUEST_TIMEOUT', 120))
    AI_MAX_TOKENS = int(os.getenv('AI_MAX_TOKENS', 1000))
    
    # Logging
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE = os.getenv('LOG_FILE', '/tmp/dashboard.log')
    
    @staticmethod
    def get_current_date():
        """Get current date in readable format"""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %A")
    
    @classmethod
    def validate(cls):
        """Validate critical configuration"""
        warnings = []
        
        if not cls.OPEN_WEB_UI_API_KEY:
            warnings.append("OPEN_WEB_UI_API_KEY not set - AI suggestions will be unavailable")
        
        if not cls.WEATHER_API_KEY:
            warnings.append("WEATHER_API_KEY not set - Weather data will be unavailable")
        
        if not cls.GARMIN_EMAIL or not cls.GARMIN_PASSWORD:
            warnings.append("Garmin credentials not set - Fitness data will be unavailable")
        
        if not os.path.exists(cls.CREDENTIALS_FILE):
            warnings.append(f"{cls.CREDENTIALS_FILE} not found - Google Calendar will be unavailable")
        
        return warnings


class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True


class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False


class TestConfig(Config):
    """Test configuration"""
    TESTING = True
    DEBUG = True


# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'test': TestConfig,
    'default': DevelopmentConfig
}
