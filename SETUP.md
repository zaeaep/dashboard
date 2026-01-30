# 🚀 Quick Setup Guide

This guide will help you set up the Personal Dashboard on a fresh system.

## 📋 Prerequisites

- Python 3.8 or higher
- Git
- Internet connection

## ⚡ Quick Start (5 minutes)

### 1. Clone and Install

```bash
# Clone the repository
git clone <your-repository-url>
cd OpenWebUI

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
# Copy example environment file
cp .env.example .env

# Edit with your favorite editor
nano .env  # or vim .env, or code .env
```

**Minimal required settings to get started:**
```env
# Get from https://openweathermap.org/api (free tier available)
WEATHER_API_KEY=your_weather_api_key_here
WEATHER_CITY=YourCity

# For AI features (optional on first run)
OPEN_WEB_UI_API_KEY=your_api_key_here
```

### 3. Google Calendar Setup (Optional but Recommended)

1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Create a new project
3. Enable **Google Calendar API**
4. Create **OAuth 2.0 credentials**:
   - Application type: **Desktop app**
   - Download the JSON file
5. Save as `credentials.json` in the project root

```bash
# Copy example credentials (or use your downloaded one)
cp credentials.example.json credentials.json
# Edit with your actual Google OAuth credentials
```

### 4. Prepare Data Files

```bash
# Create data directory and copy example events
mkdir -p data
cp data/local_events.example.json data/local_events.json
```

### 5. Run the Dashboard

```bash
# Start the server
python run.py

# Or use the startup script
./scripts/start_dashboard.sh
```

Access at: **http://localhost:5000**

## 🔑 Getting API Keys

### OpenWeatherMap (FREE - Required for weather)
1. Visit: https://openweathermap.org/api
2. Sign up for free account
3. Get API key from dashboard
4. Add to `.env`: `WEATHER_API_KEY=your_key`

### Open Web UI (Optional - For AI suggestions)
1. Get from your Open Web UI instance
2. Or use any OpenAI-compatible API
3. Add to `.env`: `OPEN_WEB_UI_API_KEY=your_key`

### Garmin Connect (Optional - For fitness data)
1. Have an active Garmin account
2. Add credentials to `.env`:
   ```env
   GARMIN_EMAIL=your_email@example.com
   GARMIN_PASSWORD=your_password
   ```

## 📁 File Structure Overview

```
OpenWebUI/
├── .env                    # Your config (create from .env.example)
├── .env.example           # Template with all settings
├── credentials.json       # Google OAuth (create from example)
├── credentials.example.json
├── requirements.txt       # Python dependencies
├── run.py                # Start the app
├── app/                  # Application code
│   ├── templates/        # Dashboard HTML
│   ├── routes/          # API endpoints
│   └── services/        # Business logic
├── data/
│   ├── local_events.json          # Your events
│   └── local_events.example.json  # Example template
└── scripts/
    ├── start_dashboard.sh
    └── stop_dashboard.sh
```

## 🎨 Dashboard Features

### Current Widgets:
- ☀️ **Weather** - Real-time weather data
- 📅 **Google Calendar** - Today's schedule & upcoming events
- 💪 **Garmin Fitness** - Sleep, training load, fitness status
- ✅ **Todo List** - Integrated with Google Calendar
- ⏰ **Timer** - Countdown timer with notifications
- 🤖 **AI Suggestions** - Personalized recommendations

### Settings:
- Toggle widgets on/off
- Customize page background color
- All preferences saved locally

## 🔧 Troubleshooting

### Dashboard won't start
```bash
# Check Python version
python --version  # Should be 3.8+

# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

### Google Calendar not working
1. Check `credentials.json` exists in project root
2. Delete `token.pickle` if exists
3. Restart app - browser will open for OAuth
4. Grant calendar permissions

### Weather not showing
1. Verify API key in `.env`
2. Check city name spelling
3. Test API key: https://openweathermap.org/api

### AI suggestions not working
- This feature is optional
- Requires valid `OPEN_WEB_UI_API_KEY`
- Dashboard works fine without it

## 🚀 Production Deployment

### Important Security Steps:

1. **Change SECRET_KEY**:
   ```bash
   python -c "import secrets; print(secrets.token_hex(32))"
   ```
   Add output to `.env` as `SECRET_KEY=...`

2. **Set DEBUG to False**:
   ```env
   DEBUG=False
   ```

3. **Use proper web server**:
   ```bash
   # Install gunicorn
   pip install gunicorn
   
   # Run with gunicorn
   gunicorn -w 4 -b 0.0.0.0:5000 "app:create_app()"
   ```

4. **Set up HTTPS** with nginx/Apache reverse proxy

5. **Never commit**:
   - `.env` file
   - `credentials.json`
   - `token.pickle`
   - `data/local_events.json` (contains your personal data)

## 📚 Next Steps

1. ✅ Get the dashboard running
2. ✅ Configure Google Calendar integration
3. ✅ Customize widgets in settings
4. ✅ Add your local events to `data/local_events.json`
5. ✅ Set up keyboard shortcuts (see main README.md)
6. 🎉 Enjoy your personalized dashboard!

## 🐛 Need Help?

- Check logs: `tail -f /tmp/dashboard.log`
- Review main README.md for detailed documentation
- Verify all API keys are correct in `.env`

## 📝 License

See LICENSE file in repository.
