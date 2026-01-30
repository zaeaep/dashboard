import os
import json
import requests
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo
from dotenv import load_dotenv
from flask import Flask, jsonify, render_template
from flask_cors import CORS
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import pickle

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)

# API Keys
API_KEY = os.getenv("OPEN_WEB_UI_API_KEY")
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")  # Get from openweathermap.org
GARMIN_EMAIL = os.getenv("GARMIN_EMAIL")
GARMIN_PASSWORD = os.getenv("GARMIN_PASSWORD")

# Google Calendar Setup
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']

# Calendar filter - specify which calendars to include
# Leave empty [] to include ALL calendars
# Or add calendar names/IDs you want to include, for example:
# CALENDAR_FILTER = ["Work", "Personal", "john.doe@gmail.com"]
CALENDAR_FILTER = []  # Empty = include all calendars

# Chat completion function (imported from your existing code)
def get_ai_suggestion(prompt):
    """Get AI suggestions using the Open Web UI API"""
    BASE_URL = "https://openwebui.uni-freiburg.de"
    CHAT_ENDPOINT = "/api/v1/chat/completions"
    url = f"{BASE_URL}{CHAT_ENDPOINT}"
    
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }
    
    payload = {
        "model": "openai/gpt-5.2-llmlb",
        "messages": [
            {"role": "user", "content": prompt}
        ],
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=120)
        if response.status_code == 200:
            data = response.json()
            result = data["choices"][0]["message"]["content"]
            print(f"✓ AI response received ({len(result)} chars)")
            return result
        else:
            error_msg = f"API Error {response.status_code}"
            try:
                error_data = response.json()
                error_msg += f": {error_data.get('error', {}).get('message', error_data)}"
            except:
                error_msg += f": {response.text[:200]}"
            
            print(f"⚠️  LLM {error_msg}")
            return f"AI suggestions unavailable (Error {response.status_code}). Check API key and model name."
    except requests.Timeout:
        print("⚠️  LLM request timed out")
        return "AI suggestions timed out. Please refresh to try again."
    except Exception as e:
        print(f"⚠️  LLM error: {str(e)}")
        return f"AI suggestions error: {str(e)}"


def get_google_calendar_events():
    """Get Google Calendar events for the next 2 months"""
    
    # Check if credentials.json exists
    if not os.path.exists('credentials.json'):
        print("⚠️  credentials.json not found. Google Calendar integration disabled.")
        print("   See README_DASHBOARD.md for setup instructions.")
        return []
    
    creds = None
    
    # Token file stores user's access and refresh tokens
    if os.path.exists('token.pickle'):
        try:
            with open('token.pickle', 'rb') as token:
                creds = pickle.load(token)
        except Exception as e:
            print(f"Error loading token.pickle: {e}")
            creds = None
    
    # If credentials don't exist or are invalid, let the user log in
    if not creds or not creds.valid:
        try:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', SCOPES)
                creds = flow.run_local_server(port=0)
            
            # Save credentials for next run
            with open('token.pickle', 'wb') as token:
                pickle.dump(creds, token)
        except Exception as e:
            print(f"Error during Google Calendar authentication: {e}")
            return []
    
    try:
        service = build('calendar', 'v3', credentials=creds)
        
        # Get all calendars
        calendar_list = service.calendarList().list().execute()
        all_calendars = calendar_list.get('items', [])
        
        # Filter calendars if CALENDAR_FILTER is specified
        if CALENDAR_FILTER:
            filtered_calendars = [
                cal for cal in all_calendars
                if cal['summary'] in CALENDAR_FILTER or cal['id'] in CALENDAR_FILTER
            ]
            print(f"📅 Using {len(filtered_calendars)} of {len(all_calendars)} calendars")
        else:
            filtered_calendars = all_calendars
            print(f"📅 Using all {len(filtered_calendars)} calendars")
        
        # Get events for the next 2 months
        now = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
        two_months = (datetime.now(timezone.utc) + timedelta(days=60)).isoformat().replace('+00:00', 'Z')
        
        all_events = []
        
        # Fetch events from each calendar
        for calendar in filtered_calendars:
            try:
                calendar_id = calendar['id']
                calendar_name = calendar['summary']
                
                events_result = service.events().list(
                    calendarId=calendar_id,
                    timeMin=now,
                    timeMax=two_months,
                    maxResults=100,
                    singleEvents=True,
                    orderBy='startTime'
                ).execute()
                
                events = events_result.get('items', [])
                
                # Format events with calendar name
                for event in events:
                    start = event['start'].get('dateTime', event['start'].get('date'))
                    all_events.append({
                        'summary': event.get('summary', 'No title'),
                        'start': start,
                        'end': event['end'].get('dateTime', event['end'].get('date')),
                        'description': event.get('description', ''),
                        'calendar': calendar_name
                    })
                
            except Exception as e:
                print(f"   Error fetching '{calendar.get('summary', 'Unknown')}': {e}")
                continue
        
        # Sort all events by start time
        all_events.sort(key=lambda x: x['start'])
        
        print(f"✓ Fetched {len(all_events)} total events\n")
        return all_events
        
    except Exception as e:
        print(f"Error fetching calendars: {e}")
        return []


def get_weather():
    """Get weather from OpenWeatherMap API"""
    if not WEATHER_API_KEY:
        print("⚠️  Weather API key not configured")
        return {
            "temperature": 15,
            "feels_like": 13,
            "description": "configure weather API key",
            "humidity": 60,
            "wind_speed": 3.5,
            "city": "Not configured"
        }
    
    # Default to Freiburg, Germany - update with your location
    city = "Freiburg"
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API_KEY}&units=metric"
    
    try:
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            return {
                "temperature": data["main"]["temp"],
                "feels_like": data["main"]["feels_like"],
                "description": data["weather"][0]["description"],
                "humidity": data["main"]["humidity"],
                "wind_speed": data["wind"]["speed"],
                "city": city
            }
        else:
            print(f"⚠️  Weather API error {response.status_code} (New API keys can take 1-2 hours to activate)")
            return {
                "temperature": 15,
                "feels_like": 13,
                "description": "weather API error",
                "humidity": 60,
                "wind_speed": 3.5,
                "city": city
            }
    except Exception as e:
        print(f"⚠️  Weather error: {str(e)}")
        return {
            "temperature": 15,
            "feels_like": 13,
            "description": "weather unavailable",
            "humidity": 60,
            "wind_speed": 3.5,
            "city": city
        }


def get_garmin_data():
    """Get Garmin training plan and sleep score
    Note: This requires Garmin API credentials or garminconnect library
    """
    
    if not GARMIN_EMAIL or not GARMIN_PASSWORD:
        print("⚠️  Garmin credentials not configured in .env file")
        return {
            "sleep_score": "Not configured",
            "sleep_hours": 0,
            "training_load": "N/A",
            "training_status": "Configure Garmin credentials in .env",
        }
    
    try:
        from garminconnect import Garmin
        
        client = Garmin(GARMIN_EMAIL, GARMIN_PASSWORD)
        client.login()
        
        # Get today's date
        today = datetime.now().strftime("%Y-%m-%d")
        
        # Get sleep data
        sleep_data = client.get_sleep_data(today)
        
        # Try multiple methods to get training data
        training_status = None
        training_load = 'N/A'
        training_key = 'N/A'
        
        try:
            training_status = client.get_training_status(today)
        except Exception as e:
            print(f"⚠️  Training status unavailable: {e}")
        
        # Try alternative method - get stats
        try:
            stats = client.get_stats(today)
            if stats:
                training_load = stats.get('trainingLoad', stats.get('userDayPeak', 'N/A'))
        except:
            pass
        
        print(f"✓ Garmin data synced\n")
        
        # Extract sleep score
        sleep_score = 'N/A'
        sleep_seconds = 0
        if sleep_data and 'dailySleepDTO' in sleep_data:
            daily_sleep = sleep_data['dailySleepDTO']
            if 'sleepScores' in daily_sleep and 'overall' in daily_sleep['sleepScores']:
                sleep_score = daily_sleep['sleepScores']['overall'].get('value', 'N/A')
            if 'sleepTimeSeconds' in daily_sleep:
                sleep_seconds = daily_sleep['sleepTimeSeconds']
        
        # Extract training info if we got it
        if training_status and 'mostRecentTrainingStatus' in training_status:
            latest_status = training_status['mostRecentTrainingStatus'].get('latestTrainingStatusData', {})
            # Get first device's data (Garmin can have multiple devices)
            if latest_status:
                device_data = next(iter(latest_status.values()), None)
                if device_data:
                    # Get acute training load
                    acute_load_dto = device_data.get('acuteTrainingLoadDTO', {})
                    training_load = acute_load_dto.get('dailyTrainingLoadAcute', 
                                   acute_load_dto.get('dailyTrainingLoadChronic', 'N/A'))
                    
                    # Get training status phrase
                    training_key = device_data.get('trainingStatusFeedbackPhrase', 
                                   device_data.get('trainingStatus', 'N/A'))
        
        return {
            "sleep_score": sleep_score,
            "sleep_hours": sleep_seconds / 3600,
            "training_load": training_load,
            "training_status": training_key,
        }
    except ImportError:
        print("⚠️  garminconnect library not installed (pip install garminconnect)")
        return {
            "sleep_score": "Install garminconnect",
            "sleep_hours": 0,
            "training_load": "N/A",
            "training_status": "pip install garminconnect",
        }
    except Exception as e:
        print(f"⚠️  Garmin error: {str(e)}")
        return {
            "sleep_score": "Connection failed",
            "sleep_hours": 0,
            "training_load": "N/A",
            "training_status": "Check credentials",
            "error": str(e)
        }


@app.route('/')
def index():
    """Serve the dashboard HTML"""
    return render_template('dashboard.html')


@app.route('/api/dashboard')
def get_dashboard_data():
    """Get all dashboard data"""
    
    try:
        # Fetch all data
        calendar_events = get_google_calendar_events()
        weather = get_weather()
        garmin = get_garmin_data()
        
        # Get today's events (using MEZ timezone)
        mez = ZoneInfo("Europe/Berlin")  # MEZ/CEST timezone
        today = datetime.now(mez).date()
        today_events = []
        
        for e in calendar_events:
            try:
                start_str = e['start']
                # Handle both date and dateTime formats
                if 'T' in start_str:
                    # DateTime format - convert to MEZ timezone
                    event_datetime = datetime.fromisoformat(start_str.replace('Z', '+00:00'))
                    event_date = event_datetime.astimezone(mez).date()
                else:
                    # Date-only format - these are all-day events
                    event_date = datetime.fromisoformat(start_str).date()
                
                if event_date == today:
                    today_events.append(e)
            except Exception as ex:
                continue
        
        print(f"✓ Found {len(today_events)} event(s) for today\n")
        
        # Prepare context for AI
        context = f"""
        Today's date: {datetime.now().strftime('%Y-%m-%d %A')}
        
        Weather: {weather.get('temperature', 'N/A')}°C, {weather.get('description', 'N/A')}
        
        Sleep Score: {garmin.get('sleep_score', 'N/A')}
        Sleep Hours: {garmin.get('sleep_hours', 'N/A')}
        Training Status: {garmin.get('training_status', 'N/A')}
        
        Today's Calendar Events:
        {json.dumps(today_events, indent=2) if today_events else "No events scheduled"}
        
        Upcoming Events (next 2 months):
        {json.dumps(calendar_events[:10], indent=2) if calendar_events else "No upcoming events"}
        """
        
        # Get AI suggestions
        print("🤖 Generating AI suggestions...")
        
        day_plan = get_ai_suggestion(
            f"{context}\n\nBased on this information, create a personalized day plan for me. "
            "Consider my sleep quality, weather, and scheduled events. Be specific and actionable."
        )
        
        freetime_suggestions = get_ai_suggestion(
            f"{context}\n\nSuggest 3-5 activities I could do in my free time today, "
            "considering the weather and my energy levels based on sleep data."
        )
        
        nutrition_advice = get_ai_suggestion(
            f"{context}\n\nProvide personalized nutrition suggestions for today based on my "
            "training status, sleep quality, and activity level. Include meal ideas and hydration tips."
        )
        
        print("✓ AI suggestions complete\n")
        
        return jsonify({
            "timestamp": datetime.now().isoformat(),
            "weather": weather,
            "garmin": garmin,
            "calendar": {
                "today": today_events,
                "upcoming": calendar_events  # Show all events, not just first 10
            },
            "ai_suggestions": {
                "day_plan": day_plan,
                "freetime": freetime_suggestions,
                "nutrition": nutrition_advice
            }
        })
    except Exception as e:
        print(f"Error in get_dashboard_data: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            "error": str(e),
            "timestamp": datetime.now().isoformat(),
            "weather": {"temperature": 15, "feels_like": 13, "description": "error", "humidity": 60, "wind_speed": 3.5, "city": "N/A"},
            "garmin": {"sleep_score": "N/A", "sleep_hours": 0, "training_load": "N/A", "training_status": "N/A"},
            "calendar": {"today": [], "upcoming": []},
            "ai_suggestions": {
                "day_plan": "Dashboard is starting up. Please configure API keys.",
                "freetime": "See README_DASHBOARD.md for setup instructions.",
                "nutrition": "Configure your API keys to get personalized suggestions."
            }
        }), 200


@app.route('/api/refresh')
def refresh_data():
    """Manually refresh all data"""
    return get_dashboard_data()


def get_context_data():
    """Helper function to get context data for AI suggestions"""
    calendar_events = get_google_calendar_events()
    weather = get_weather()
    garmin = get_garmin_data()
    
    mez = ZoneInfo("Europe/Berlin")
    today = datetime.now(mez).date()
    today_events = [e for e in calendar_events 
                   if datetime.fromisoformat(e['start'].replace('Z', '+00:00').split('T')[0]).date() == today]
    
    context = f"""
    Today's date: {datetime.now().strftime('%Y-%m-%d %A')}
    
    Weather: {weather.get('temperature', 'N/A')}°C, {weather.get('description', 'N/A')}
    
    Sleep Score: {garmin.get('sleep_score', 'N/A')}
    Sleep Hours: {garmin.get('sleep_hours', 'N/A')}
    Training Status: {garmin.get('training_status', 'N/A')}
    
    Today's Calendar Events:
    {json.dumps(today_events, indent=2) if today_events else "No events scheduled"}
    
    Upcoming Events (next 2 months):
    {json.dumps(calendar_events[:10], indent=2) if calendar_events else "No upcoming events"}
    """
    return context


@app.route('/api/ai/day-plan')
def get_day_plan():
    """Get personalized day plan"""
    try:
        context = get_context_data()
        day_plan = get_ai_suggestion(
            f"{context}\n\nBased on this information, create a personalized day plan for me. "
            "Consider my sleep quality, weather, and scheduled events. Be specific and actionable."
        )
        return jsonify({"suggestion": day_plan})
    except Exception as e:
        return jsonify({"error": str(e), "suggestion": f"Error generating day plan: {str(e)}"}), 200


@app.route('/api/ai/freetime')
def get_freetime():
    """Get free time suggestions"""
    try:
        context = get_context_data()
        freetime = get_ai_suggestion(
            f"{context}\n\nSuggest 3-5 activities I could do in my free time today, "
            "considering the weather and my energy levels based on sleep data."
        )
        return jsonify({"suggestion": freetime})
    except Exception as e:
        return jsonify({"error": str(e), "suggestion": f"Error generating suggestions: {str(e)}"}), 200


@app.route('/api/ai/nutrition')
def get_nutrition():
    """Get nutrition recommendations"""
    try:
        context = get_context_data()
        nutrition = get_ai_suggestion(
            f"{context}\n\nProvide personalized nutrition suggestions for today based on my "
            "training status, sleep quality, and activity level. Include meal ideas and hydration tips."
        )
        return jsonify({"suggestion": nutrition})
    except Exception as e:
        return jsonify({"error": str(e), "suggestion": f"Error generating nutrition advice: {str(e)}"}), 200


if __name__ == '__main__':
    print("🚀 Starting Personal Dashboard...")
    print("📊 Access your dashboard at: http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)
