"""
API routes for the Personal Dashboard.
"""
import json
from datetime import datetime
from flask import Blueprint, jsonify, render_template, request

from ..services import AIService, CalendarService, GarminService, WeatherService, EventService
from ..config import Config
from ..utils import setup_logger, now_in_timezone

logger = setup_logger(__name__)

# Create blueprint
api_bp = Blueprint('api', __name__)

# Initialize services
ai_service = AIService()
calendar_service = CalendarService()
garmin_service = GarminService()
weather_service = WeatherService()
event_service = EventService()


def _build_context() -> str:
    """Build context string for AI suggestions"""
    calendar_events = calendar_service.get_events()
    weather = weather_service.get_weather()
    garmin = garmin_service.get_data()
    today_events = calendar_service.get_today_events(calendar_events)
    
    context = f"""
Today's date: {datetime.now().strftime('%Y-%m-%d %A')}

Weather: {weather.get('temperature', 'N/A')}°C, {weather.get('description', 'N/A')}

Sleep Score: {garmin.get('sleep_score', 'N/A')}
Sleep Hours: {garmin.get('sleep_hours', 'N/A')}
Training Status: {garmin.get('training_status', 'N/A')}

Today's Calendar Events:
{json.dumps(today_events, indent=2) if today_events else "No events scheduled"}

Upcoming Events (next {Config.CALENDAR_MONTHS_AHEAD} months):
{json.dumps(calendar_events[:10], indent=2) if calendar_events else "No upcoming events"}
"""
    return context


@api_bp.route('/')
def index():
    """Serve the dashboard HTML"""
    return render_template('dashboard.html')


@api_bp.route('/api/dashboard')
def get_dashboard_data():
    """Get all dashboard data"""
    try:
        logger.info("Fetching dashboard data...")
        
        # Fetch all data
        calendar_events = calendar_service.get_events()
        weather = weather_service.get_weather()
        garmin = garmin_service.get_data()
        today_events = calendar_service.get_today_events(calendar_events)
        
        # Build context for AI
        context = _build_context()
        
        # Get AI suggestions
        logger.info("Generating AI suggestions...")
        day_plan = ai_service.get_day_plan(context)
        freetime = ai_service.get_freetime_suggestions(context)
        nutrition = ai_service.get_nutrition_advice(context)
        logger.info("AI suggestions complete")
        
        return jsonify({
            "timestamp": datetime.now().isoformat(),
            "weather": weather,
            "garmin": garmin,
            "calendar": {
                "today": today_events,
                "upcoming": calendar_events
            },
            "ai_suggestions": {
                "day_plan": day_plan,
                "freetime": freetime,
                "nutrition": nutrition
            }
        })
    
    except Exception as e:
        logger.error(f"Error in get_dashboard_data: {e}", exc_info=True)
        return jsonify({
            "error": str(e),
            "timestamp": datetime.now().isoformat(),
            "weather": weather_service._get_fallback_weather("error"),
            "garmin": garmin_service._get_fallback_data("error"),
            "calendar": {"today": [], "upcoming": []},
            "ai_suggestions": {
                "day_plan": "Dashboard is starting up. Please check configuration.",
                "freetime": "See README.md for setup instructions.",
                "nutrition": "Configure your API keys to get personalized suggestions."
            }
        }), 200


@api_bp.route('/api/dashboard/quick')
def get_quick_data():
    """Get quick dashboard data without AI suggestions"""
    try:
        logger.info("Fetching quick dashboard data...")
        
        # Fetch non-AI data (fast)
        calendar_events = calendar_service.get_events()
        weather = weather_service.get_weather()
        garmin = garmin_service.get_data()
        today_events = calendar_service.get_today_events(calendar_events)
        
        logger.info("Quick data fetched successfully")
        
        return jsonify({
            "timestamp": datetime.now().isoformat(),
            "weather": weather,
            "garmin": garmin,
            "calendar": {
                "today": today_events,
                "upcoming": calendar_events
            }
        })
    
    except Exception as e:
        logger.error(f"Error in get_quick_data: {e}", exc_info=True)
        return jsonify({
            "error": str(e),
            "timestamp": datetime.now().isoformat(),
            "weather": weather_service._get_fallback_weather("error"),
            "garmin": garmin_service._get_fallback_data("error"),
            "calendar": {"today": [], "upcoming": []}
        }), 200


@api_bp.route('/api/refresh')
def refresh_data():
    """Manually refresh all data"""
    return get_dashboard_data()


@api_bp.route('/api/ai/day-plan')
def get_day_plan():
    """Get personalized day plan"""
    try:
        context = _build_context()
        day_plan = ai_service.get_day_plan(context)
        return jsonify({"suggestion": day_plan})
    except Exception as e:
        logger.error(f"Error generating day plan: {e}")
        return jsonify({
            "error": str(e),
            "suggestion": f"Error generating day plan: {str(e)}"
        }), 200


@api_bp.route('/api/ai/freetime')
def get_freetime():
    """Get free time suggestions"""
    try:
        context = _build_context()
        freetime = ai_service.get_freetime_suggestions(context)
        return jsonify({"suggestion": freetime})
    except Exception as e:
        logger.error(f"Error generating freetime suggestions: {e}")
        return jsonify({
            "error": str(e),
            "suggestion": f"Error generating suggestions: {str(e)}"
        }), 200


@api_bp.route('/api/ai/nutrition')
def get_nutrition():
    """Get nutrition recommendations"""
    try:
        context = _build_context()
        nutrition = ai_service.get_nutrition_advice(context)
        return jsonify({"suggestion": nutrition})
    except Exception as e:
        logger.error(f"Error generating nutrition advice: {e}")
        return jsonify({
            "error": str(e),
            "suggestion": f"Error generating nutrition advice: {str(e)}"
        }), 200


@api_bp.route('/api/weather/details')
def get_weather_details():
    """Get detailed weather information"""
    try:
        weather = weather_service.get_weather()
        # Add additional details if available
        return jsonify({
            "temperature": weather.get('temperature', 15),
            "feels_like": weather.get('feels_like', 13),
            "description": weather.get('description', 'N/A'),
            "humidity": weather.get('humidity', 60),
            "wind_speed": weather.get('wind_speed', 3.5),
            "wind_direction": weather.get('wind_direction', 0),
            "pressure": weather.get('pressure', 1013),
            "visibility": weather.get('visibility', 10000),
            "clouds": weather.get('clouds', 0),
            "temp_min": weather.get('temp_min', weather.get('temperature', 15) - 2),
            "temp_max": weather.get('temp_max', weather.get('temperature', 15) + 2),
            "sunrise": weather.get('sunrise', 0),
            "sunset": weather.get('sunset', 0),
            "city": weather.get('city', 'Unknown'),
            "country": weather.get('country', 'N/A'),
            "lat": weather.get('lat', 0),
            "lon": weather.get('lon', 0)
        })
    except Exception as e:
        logger.error(f"Error getting weather details: {e}")
        return jsonify({"error": str(e)}), 200


@api_bp.route('/api/garmin/details')
def get_garmin_details():
    """Get detailed Garmin fitness information"""
    try:
        garmin = garmin_service.get_data()
        return jsonify({
            "sleep_score": garmin.get('sleep_score', 'N/A'),
            "sleep_hours": garmin.get('sleep_hours', 0),
            "training_load": garmin.get('training_load', 'N/A'),
            "training_status": garmin.get('training_status', 'N/A'),
            "steps": garmin.get('steps', 'N/A'),
            "calories": garmin.get('calories', 'N/A'),
            "heart_rate": garmin.get('heart_rate', 'N/A'),
            "body_battery": garmin.get('body_battery_current') is not None,
            "body_battery_current": garmin.get('body_battery_current', 'N/A'),
            "body_battery_highest": garmin.get('body_battery_highest', 'N/A'),
            "body_battery_lowest": garmin.get('body_battery_lowest', 'N/A')
        })
    except Exception as e:
        logger.error(f"Error getting Garmin details: {e}")
        return jsonify({"error": str(e)}), 200


@api_bp.route('/api/sleep/analysis')
def get_sleep_analysis():
    """Get detailed sleep analysis with weekly trends"""
    try:
        days = int(request.args.get('days', 7))  # Default to 7 days
        analysis = garmin_service.get_sleep_analysis(days=days)
        return jsonify(analysis)
    except Exception as e:
        logger.error(f"Error getting sleep analysis: {e}")
        return jsonify({"error": str(e)}), 200


@api_bp.route('/api/events/local')
def get_local_events():
    """Get local sports and fitness events with optional keyword filtering"""
    try:
        days = int(request.args.get('days', 60))  # Default to 60 days ahead
        keywords_param = request.args.get('keywords', '')
        
        # Parse keywords (comma-separated)
        keywords = [k.strip() for k in keywords_param.split(',') if k.strip()] if keywords_param else None
        
        events = event_service.get_events(days_ahead=days, keywords=keywords)
        categories = event_service.get_event_categories()
        types = event_service.get_event_types()
        
        return jsonify({
            "events": events,
            "total": len(events),
            "categories": categories,
            "types": types,
            "filters": {
                "days": days,
                "keywords": keywords
            }
        })
    except Exception as e:
        logger.error(f"Error getting local events: {e}")
        return jsonify({"error": str(e), "events": [], "total": 0}), 200


@api_bp.route('/api/events/search')
def search_events_online():
    """Search for real events from the web"""
    try:
        keywords = request.args.get('keywords', '')
        location = request.args.get('location', Config.WEATHER_CITY or 'your area')
        
        if not keywords:
            return jsonify({"error": "Keywords parameter required", "events": []}), 400
        
        logger.info(f"Searching web for events: {keywords} in {location}")
        
        # Search for real events from the web
        web_events = event_service.search_web_events(keywords, location)
        
        return jsonify({
            "keywords": keywords,
            "location": location,
            "events": web_events,
            "total": len(web_events),
            "source": "web_search"
        })
    except Exception as e:
        logger.error(f"Error searching events online: {e}")
        return jsonify({
            "error": str(e),
            "events": [],
            "total": 0
        }), 200


@api_bp.route('/api/todos', methods=['GET'])
def get_todos():
    """Get all todos"""
    try:
        todos = calendar_service.get_todos()
        return jsonify(todos)
    except Exception as e:
        logger.error(f"Error getting todos: {e}")
        return jsonify({"error": str(e)}), 500


@api_bp.route('/api/todos', methods=['POST'])
def create_todo():
    """Create a new todo and add it to Google Calendar"""
    try:
        data = request.json
        title = data.get('title')
        date = data.get('date')
        time = data.get('time', '12:00')
        completed = data.get('completed', False)
        
        if not title or not date:
            return jsonify({"error": "Title and date are required"}), 400
        
        # Create todo in Google Calendar
        todo = calendar_service.create_todo(title, date, time, completed)
        
        return jsonify(todo), 201
    except Exception as e:
        logger.error(f"Error creating todo: {e}")
        return jsonify({"error": str(e)}), 500


@api_bp.route('/api/todos/<todo_id>', methods=['PATCH'])
def update_todo(todo_id):
    """Update a todo (e.g., mark as completed)"""
    try:
        data = request.json
        completed = data.get('completed')
        
        if completed is None:
            return jsonify({"error": "Completed status required"}), 400
        
        updated_todo = calendar_service.update_todo(todo_id, completed)
        
        return jsonify(updated_todo)
    except Exception as e:
        logger.error(f"Error updating todo: {e}")
        return jsonify({"error": str(e)}), 500


@api_bp.route('/api/todos/<todo_id>', methods=['DELETE'])
def delete_todo(todo_id):
    """Delete a todo from Google Calendar"""
    try:
        calendar_service.delete_todo(todo_id)
        return jsonify({"success": True, "message": "Todo deleted"}), 200
    except Exception as e:
        logger.error(f"Error deleting todo: {e}")
        return jsonify({"error": str(e)}), 500
