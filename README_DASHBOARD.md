# Personal Dashboard Setup Guide

## 🚀 Quick Start

This dashboard integrates Google Calendar, Garmin data, weather information, and AI-powered suggestions to help you plan your day.

## 📋 Prerequisites

1. Python 3.8 or higher
2. Google Calendar API credentials
3. OpenWeatherMap API key (free tier available)
4. Garmin Connect account (optional)
5. Open Web UI API key (you already have this)

## 🔧 Installation Steps

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Create or update your `.env` file with the following:

```env
# Open Web UI API (you already have this)
OPEN_WEB_UI_API_KEY=your_existing_key_here

# Weather API (get free key from https://openweathermap.org/api)
WEATHER_API_KEY=your_weather_api_key_here

# Garmin (optional - for training and sleep data)
GARMIN_EMAIL=your_garmin_email@example.com
GARMIN_PASSWORD=your_garmin_password
```

### 3. Setup Google Calendar API

#### Step-by-step:

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project (or select existing)
3. Enable the Google Calendar API:
   - Go to "APIs & Services" > "Library"
   - Search for "Google Calendar API"
   - Click "Enable"
4. Create OAuth 2.0 credentials:
   - Go to "APIs & Services" > "Credentials"
   - Click "Create Credentials" > "OAuth client ID"
   - Select "Desktop app" as application type
   - Download the JSON file
   - Save it as `credentials.json` in the `/home/seli/OpenWebUI` directory

### 4. Get OpenWeatherMap API Key

1. Sign up at [OpenWeatherMap](https://openweathermap.org/api)
2. Get your free API key (Current Weather Data plan is free)
3. Add it to your `.env` file

### 5. Configure Garmin (Optional)

If you want Garmin training and sleep data:
- Add your Garmin Connect credentials to `.env`
- The dashboard will work without Garmin, showing placeholder data

## 🏃 Running the Dashboard

```bash
python3 dashboard.py
```

The first time you run it:
- A browser window will open for Google Calendar authentication
- Grant the necessary permissions
- Credentials will be saved in `token.pickle` for future use

## 🌐 Access Your Dashboard

Open your browser and go to:
```
http://localhost:5000
```

## 📱 Features

### ✅ Current Features:
- **Real-time Weather**: Temperature, conditions, humidity, wind speed
- **Sleep Analytics**: Garmin sleep score and duration
- **Training Status**: Current training load and recommendations
- **Today's Schedule**: All events from Google Calendar for today
- **AI Day Planner**: Personalized suggestions based on your data
- **Free Time Ideas**: AI-generated activities based on weather and energy
- **Nutrition Advice**: Customized meal and hydration recommendations
- **Upcoming Events**: Next 2 months of calendar events

### 🔄 Auto-Refresh:
- Dashboard automatically refreshes every 15 minutes
- Manual refresh button available

## 🛠️ Customization

### Change Your Location (Weather):
Edit line 103 in `dashboard.py`:
```python
city = "Freiburg"  # Change to your city
```

### Adjust AI Model:
Edit line 40 in `dashboard.py` to use a different model:
```python
"model": "openai/gpt-5.2-llmlb",  # Change model here
```

### Customize Refresh Interval:
Edit line 486 in `templates/dashboard.html`:
```javascript
setInterval(loadDashboard, 15 * 60 * 1000);  // Currently 15 minutes
```

## 🔍 Troubleshooting

### Google Calendar not working:
- Ensure `credentials.json` is in the correct directory
- Delete `token.pickle` and re-authenticate
- Check that Calendar API is enabled in Google Cloud Console

### Weather not showing:
- Verify your `WEATHER_API_KEY` in `.env`
- Check city name spelling in `dashboard.py`

### Garmin data unavailable:
- Install: `pip install garminconnect`
- Verify credentials in `.env`
- Dashboard will show placeholder data if Garmin fails

### AI suggestions not working:
- Check `OPEN_WEB_UI_API_KEY` in `.env`
- Verify API endpoint is accessible
- Check console for error messages

## 📊 Project Structure

```
/home/seli/OpenWebUI/
├── dashboard.py              # Main Flask backend
├── chat_completion.py        # Your original chat completion script
├── templates/
│   └── dashboard.html        # Frontend UI
├── requirements.txt          # Python dependencies
├── .env                      # Environment variables (create this)
├── credentials.json          # Google API credentials (download this)
└── token.pickle              # Auto-generated after first Google auth
```

## 🔐 Security Notes

- Never commit `.env`, `credentials.json`, or `token.pickle` to version control
- Keep your API keys private
- The dashboard runs locally (localhost:5000)

## 🎯 Next Steps

1. Get all API keys configured
2. Run `python3 dashboard.py`
3. Authenticate with Google Calendar
4. Enjoy your personalized dashboard!

## 💡 Tips

- The AI suggestions improve with more calendar data
- Set up recurring events in Google Calendar for better planning
- Check dashboard in the morning for best day planning
- Weather updates help with outdoor activity suggestions

## 🆘 Need Help?

If you encounter issues:
1. Check the terminal output for error messages
2. Verify all API keys are correct in `.env`
3. Ensure all dependencies are installed
4. Try the troubleshooting steps above

Enjoy your personalized dashboard! 🎉
