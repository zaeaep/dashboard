"""
Weather Service for fetching weather data from OpenWeatherMap API.
"""
import requests
from typing import Dict, Any
from ..config import Config
from ..utils import setup_logger, log_api_request, log_error

logger = setup_logger(__name__)


class WeatherService:
    """Service for weather data"""
    
    def __init__(self, config: Config = Config):
        self.config = config
        self.api_key = config.WEATHER_API_KEY
        self.city = config.WEATHER_CITY
        self.api_url = config.WEATHER_API_URL
    
    def get_weather(self) -> Dict[str, Any]:
        """
        Get current weather data.
        
        Returns:
            Dictionary with weather information
        """
        if not self.api_key:
            logger.warning("Weather API key not configured")
            return self._get_fallback_weather()
        
        url = f"{self.api_url}?q={self.city}&appid={self.api_key}&units=metric"
        
        try:
            response = requests.get(url, timeout=10)
            
            log_api_request(logger, 'Weather', response.status_code)
            
            if response.status_code == 200:
                data = response.json()
                return {
                    "temperature": data["main"]["temp"],
                    "feels_like": data["main"]["feels_like"],
                    "description": data["weather"][0]["description"],
                    "humidity": data["main"]["humidity"],
                    "wind_speed": data["wind"]["speed"],
                    "wind_direction": data["wind"].get("deg", 0),
                    "pressure": data["main"]["pressure"],
                    "visibility": data.get("visibility", 10000),
                    "clouds": data["clouds"].get("all", 0),
                    "temp_min": data["main"]["temp_min"],
                    "temp_max": data["main"]["temp_max"],
                    "sunrise": data["sys"]["sunrise"],
                    "sunset": data["sys"]["sunset"],
                    "city": self.city,
                    "country": data["sys"]["country"],
                    "lat": data["coord"]["lat"],
                    "lon": data["coord"]["lon"],
                    "icon": data["weather"][0]["icon"]
                }
            elif response.status_code == 401:
                logger.warning("Weather API key invalid or not activated (can take 1-2 hours)")
                return self._get_fallback_weather("API key not activated")
            else:
                logger.warning(f"Weather API returned status {response.status_code}")
                return self._get_fallback_weather("API error")
        
        except requests.Timeout:
            logger.warning("Weather API request timed out")
            return self._get_fallback_weather("Request timeout")
        
        except Exception as e:
            log_error(logger, 'Weather', e)
            return self._get_fallback_weather("Service unavailable")
    
    def _get_fallback_weather(self, reason: str = "Not configured") -> Dict[str, Any]:
        """Return fallback weather data when API is unavailable"""
        setup_message = None
        if reason == "Not configured":
            setup_message = "⚠️ Weather API not configured. Get a free API key from https://openweathermap.org/api and add it to your .env file as WEATHER_API_KEY"
        elif "API key" in reason:
            setup_message = "⚠️ Weather API key invalid. Check your WEATHER_API_KEY in .env file. Note: New keys can take 1-2 hours to activate."
        
        return {
            "temperature": 15,
            "feels_like": 13,
            "setup_required": reason,
            "setup_message": setup_message,
            "description": reason.lower(),
            "humidity": 60,
            "wind_speed": 3.5,
            "city": self.city,
            "icon": "01d"
        }
