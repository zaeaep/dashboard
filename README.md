# Personal Dashboard

A comprehensive personal dashboard integrating Google Calendar, Garmin fitness data, weather information, and AI-powered suggestions for optimal day planning.

## Features

- **Google Calendar Integration**: View events from multiple calendars with customizable filtering
- **Garmin Connect Data**: Track sleep score, training load, and fitness status
- **Weather Information**: Real-time weather data from OpenWeatherMap
- **AI-Powered Suggestions**: Personalized recommendations for:
  - Daily planning
  - Free time activities
  - Nutrition advice
- **Responsive Web Interface**: Beautiful purple gradient design with auto-refresh
- **Keyboard Shortcut Support**: Launch dashboard instantly with customizable hotkeys

## Project Structure

```
OpenWebUI/
├── app/                      # Main application package
│   ├── __init__.py          # Application factory
│   ├── config.py            # Configuration management
│   ├── routes/              # API routes
│   │   ├── __init__.py
│   │   └── api.py           # Dashboard endpoints
│   ├── services/            # Business logic services
│   │   ├── __init__.py
│   │   ├── ai_service.py    # AI/LLM integration
│   │   ├── calendar_service.py  # Google Calendar
│   │   ├── garmin_service.py    # Garmin Connect
│   │   └── weather_service.py   # OpenWeatherMap
│   ├── utils/               # Utility functions
│   │   ├── __init__.py
│   │   ├── helpers.py       # Helper functions
│   │   └── logger.py        # Logging setup
│   └── templates/           # HTML templates
│       └── dashboard.html   # Main dashboard UI
├── scripts/                 # Utility scripts
│   ├── start_dashboard.sh   # Start server
│   └── stop_dashboard.sh    # Stop server
├── tests/                   # Test suite
│   └── __init__.py
├── .env                     # Environment variables (create from .env.example)
├── .env.example            # Environment template
├── .gitignore              # Git ignore rules
├── requirements.txt        # Python dependencies
├── run.py                  # Application entry point
├── chat_completion.py      # CLI chat tool
└── README.md              # This file
```

## Installation

### 1. Prerequisites

- Python 3.8+
- pip and virtualenv
- Google Calendar API credentials (credentials.json)
- API keys for:
  - Open Web UI (or compatible LLM API)
  - OpenWeatherMap
  - Garmin Connect account

### 2. Setup

```bash
# Clone or navigate to the repository
cd OpenWebUI

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment template
cp .env.example .env

# Edit .env with your API keys and credentials
nano .env
```

### 3. Configuration

Edit `.env` file with your credentials:

```env
# AI/LLM Configuration
OPEN_WEB_UI_API_KEY=your_api_key_here
OPEN_WEB_UI_BASE_URL=https://openwebui.uni-freiburg.de
OPEN_WEB_UI_MODEL=openai/gpt-5.2-llmlb

# Weather Configuration
WEATHER_API_KEY=your_openweathermap_key
WEATHER_CITY=Freiburg

# Garmin Configuration
GARMIN_EMAIL=your_email@example.com
GARMIN_PASSWORD=your_password

# Timezone (MEZ/CEST)
TIMEZONE=Europe/Berlin

# Calendar Filter (optional - comma-separated)
# Leave empty to include all calendars
CALENDAR_FILTER=

# Flask Configuration
DEBUG=False
HOST=0.0.0.0
PORT=5000
```

### 4. Google Calendar Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project
3. Enable Google Calendar API
4. Create OAuth 2.0 credentials (Desktop app)
5. Download credentials as `credentials.json`
6. Place in project root directory

First run will open browser for OAuth authorization.

## Usage

### Running the Dashboard

#### Method 1: Direct Python

```bash
# Basic usage
python run.py

# With options
python run.py --host 0.0.0.0 --port 5000 --debug

# Production mode
python run.py --config production
```

#### Method 2: Startup Script

```bash
# Make scripts executable (first time only)
chmod +x scripts/start_dashboard.sh scripts/stop_dashboard.sh

# Start dashboard
./scripts/start_dashboard.sh

# Stop dashboard
./scripts/stop_dashboard.sh
```

#### Method 3: Keyboard Shortcut (Hyprland)

Add to `~/.config/hypr/hyprland.conf`:

```bash
bind = SUPER, D, exec, /full/path/to/OpenWebUI/scripts/start_dashboard.sh
bind = SUPER_SHIFT, D, exec, /full/path/to/OpenWebUI/scripts/stop_dashboard.sh
```

Reload config: `hyprctl reload`

### API Endpoints

- `GET /` - Dashboard UI
- `GET /api/dashboard` - Get all dashboard data
- `GET /api/refresh` - Refresh all data
- `GET /api/ai/day-plan` - Get personalized day plan
- `GET /api/ai/freetime` - Get free time suggestions
- `GET /api/ai/nutrition` - Get nutrition advice

## Configuration Options

### Calendar Filtering

To show only specific calendars, set in `.env`:

```env
CALENDAR_FILTER=Work,Personal,email@gmail.com
```

Leave empty to show all calendars.

### Time Range

Configure months to fetch from Google Calendar in `.env`:

```env
CALENDAR_MONTHS_AHEAD=2  # Default: 2 months
```

### Logging

```env
LOG_LEVEL=INFO  # DEBUG, INFO, WARNING, ERROR, CRITICAL
LOG_FILE=/tmp/dashboard.log
```

## Development

### Project Architecture

- **Application Factory Pattern**: `app/__init__.py` creates Flask app
- **Service Layer**: Business logic separated into dedicated services
- **Configuration Management**: Centralized in `app/config.py`
- **Blueprint-based Routes**: Modular route organization
- **Utility Functions**: Reusable helpers in `app/utils/`

### Running in Development Mode

```bash
python run.py --config development --debug
```

### Adding New Services

1. Create service in `app/services/your_service.py`
2. Implement service class with configuration injection
3. Register in `app/services/__init__.py`
4. Use in routes via `app/routes/api.py`

### Testing

```bash
# Run tests (when implemented)
pytest tests/

# With coverage
pytest --cov=app tests/
```

## Troubleshooting

### Dashboard won't start

```bash
# Check logs
tail -f /tmp/dashboard.log

# Check if port is in use
ss -tuln | grep 5000

# Kill existing processes
pkill -f run.py
```

### API Keys not working

- **OpenWeatherMap**: New keys take 1-2 hours to activate
- **Garmin**: Verify credentials in Garmin Connect app first
- **LLM API**: Check API key permissions and model name

### Google Calendar not showing events

```bash
# Delete token and re-authenticate
rm token.pickle
python run.py
```

### Script won't execute via keyboard shortcut

```bash
# Check execution log
cat /tmp/dashboard_startup.log

# Test script manually
bash -x scripts/start_dashboard.sh

# Verify paths in Hyprland config (use absolute paths)
```

## Security Notes

- **Never commit `.env`** or `credentials.json` to version control
- Use strong passwords for Garmin account
- Restrict API key permissions to minimum required
- Consider using a reverse proxy (nginx) for production
- Enable HTTPS for production deployment

## License

This project is for personal use. Modify as needed for your requirements.

## Support

For issues or questions:
1. Check logs: `/tmp/dashboard.log`
2. Verify configuration: `app/config.py`
3. Review service logs in terminal output

## Future Enhancements

- [ ] Unit and integration tests
- [ ] Docker containerization
- [ ] Database for historical data
- [ ] Mobile-responsive improvements
- [ ] Additional service integrations
- [ ] User authentication
- [ ] Multiple user support
- [ ] Custom themes
