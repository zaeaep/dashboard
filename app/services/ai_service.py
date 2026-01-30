"""
AI Service for generating personalized suggestions using Open Web UI API.
"""
import requests
from typing import Optional
from ..config import Config
from ..utils import setup_logger, log_api_request, log_error

logger = setup_logger(__name__)


class AIService:
    """Service for AI-powered suggestions"""
    
    def __init__(self, config: Config = Config):
        self.config = config
        self.base_url = config.OPEN_WEB_UI_BASE_URL
        self.endpoint = config.OPEN_WEB_UI_CHAT_ENDPOINT
        self.model = config.OPEN_WEB_UI_MODEL
        self.api_key = config.OPEN_WEB_UI_API_KEY
        self.timeout = config.AI_REQUEST_TIMEOUT
        self.max_tokens = config.AI_MAX_TOKENS
    
    def get_suggestion(self, prompt: str) -> str:
        """
        Get AI suggestion for given prompt.
        
        Args:
            prompt: The prompt to send to the AI
        
        Returns:
            AI-generated response text
        """
        if not self.api_key:
            logger.warning("AI API key not configured")
            return "AI suggestions unavailable. Please configure OPEN_WEB_UI_API_KEY."
        
        url = f"{self.base_url}{self.endpoint}"
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        
        payload = {
            "model": self.model,
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "max_tokens": self.max_tokens
        }
        
        try:
            response = requests.post(
                url,
                headers=headers,
                json=payload,
                timeout=self.timeout
            )
            
            log_api_request(logger, 'AI', response.status_code)
            
            if response.status_code == 200:
                data = response.json()
                result = data["choices"][0]["message"]["content"]
                logger.debug(f"AI response: {len(result)} chars")
                return result
            else:
                error_msg = f"API Error {response.status_code}"
                try:
                    error_data = response.json()
                    error_msg += f": {error_data.get('error', {}).get('message', error_data)}"
                except:
                    error_msg += f": {response.text[:200]}"
                
                logger.error(error_msg)
                return f"AI suggestions unavailable (Error {response.status_code})"
        
        except requests.Timeout:
            logger.warning("AI request timed out")
            return "AI suggestions timed out. Please try again."
        
        except Exception as e:
            log_error(logger, 'AI', e)
            return f"AI suggestions error: {str(e)}"
    
    def get_day_plan(self, context: str) -> str:
        """Generate personalized day plan"""
        prompt = (
            f"{context}\n\n"
            "Based on this information, create a personalized day plan for me. "
            "Consider my sleep quality, weather, and scheduled events. "
            "Be specific and actionable."
        )
        return self.get_suggestion(prompt)
    
    def get_freetime_suggestions(self, context: str) -> str:
        """Generate free time activity suggestions"""
        prompt = (
            f"{context}\n\n"
            "Suggest 3-5 activities I could do in my free time today, "
            "considering the weather and my energy levels based on sleep data."
        )
        return self.get_suggestion(prompt)
    
    def get_nutrition_advice(self, context: str) -> str:
        """Generate nutrition recommendations"""
        prompt = (
            f"{context}\n\n"
            "Provide personalized nutrition suggestions for today based on my "
            "training status, sleep quality, and activity level. "
            "Include meal ideas and hydration tips."
        )
        return self.get_suggestion(prompt)
    
    def search_events(self, keywords: str, location: str = "your area") -> str:
        """
        Search for local sports and fitness events based on keywords.
        
        Args:
            keywords: Search keywords (e.g., "running race", "cycling group")
            location: User's location (default: "your area")
        
        Returns:
            AI-generated list of event suggestions
        """
        prompt = (
            f"Search for local sports and fitness events based on these keywords: '{keywords}'\n"
            f"Location: {location}\n"
            f"Current date: {Config.get_current_date()}\n\n"
            "Please suggest 5-8 realistic local events that match these keywords. "
            "For each event, provide:\n"
            "- Event name\n"
            "- Type (race, group training, meetup, workshop, competition)\n"
            "- Date (within next 60 days)\n"
            "- Time\n"
            "- Location/venue\n"
            "- Brief description\n"
            "- Suggested tags\n\n"
            "Format as a clear, organized list. Focus on events that actually exist or are typical "
            "for this type of activity. Include both competitive and social/training options."
        )
        return self.get_suggestion(prompt)
