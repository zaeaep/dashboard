# Migration Guide: Old → New Structure

## Summary of Changes

The repository has been restructured from a flat, monolithic design to a professional, modular architecture. This guide explains what changed and how to use the new structure.

## What Changed

### Directory Structure

**Before:**
```
OpenWebUI/
├── dashboard.py (450+ lines, everything in one file)
├── templates/dashboard.html
├── start_dashboard.sh
├── stop_dashboard.sh
├── requirements.txt
└── .env
```

**After:**
```
OpenWebUI/
├── app/                     # Main application package
│   ├── config.py           # Centralized configuration
│   ├── routes/             # API endpoints
│   ├── services/           # Business logic (AI, Calendar, Garmin, Weather)
│   ├── utils/              # Helpers and logging
│   └── templates/          # HTML templates
├── scripts/                # Utility scripts
├── tests/                  # Test suite
├── run.py                  # New entry point
├── .gitignore             # Git ignore rules
└── README.md              # Comprehensive documentation
```

### Key Improvements

1. **Separation of Concerns**: Each service (AI, Calendar, Garmin, Weather) is in its own module
2. **Configuration Management**: All settings centralized in `app/config.py` with environment variable support
3. **Logging**: Proper logging with emoji icons and file output
4. **Error Handling**: Graceful fallbacks throughout all services
5. **Maintainability**: Easy to modify individual components without affecting others
6. **Extensibility**: Simple to add new services or features
7. **Professional Structure**: Follows Flask best practices and Python package conventions

## Migration Steps

### For Running the Dashboard

**Old way:**
```bash
python3 dashboard.py
```

**New way:**
```bash
# Method 1: Direct
python run.py

# Method 2: With options
python run.py --config development --debug

# Method 3: Script (recommended)
./scripts/start_dashboard.sh
```

### For Keyboard Shortcuts

Update your Hyprland config (`~/.config/hypr/hyprland.conf`):

**Old:**
```bash
bind = SUPER, D, exec, /home/seli/OpenWebUI/start_dashboard.sh
```

**New:**
```bash
bind = SUPER, D, exec, /home/seli/OpenWebUI/scripts/start_dashboard.sh
bind = SUPER_SHIFT, D, exec, /home/seli/OpenWebUI/scripts/stop_dashboard.sh
```

Then reload: `hyprctl reload`

### Configuration Changes

All hardcoded values have been moved to `.env`. Check `.env.example` for new options:

```env
# New configuration options available:
OPEN_WEB_UI_BASE_URL=https://openwebui.uni-freiburg.de
OPEN_WEB_UI_MODEL=openai/gpt-5.2-llmlb
WEATHER_CITY=Freiburg
TIMEZONE=Europe/Berlin
CALENDAR_MONTHS_AHEAD=2
AI_REQUEST_TIMEOUT=120
AI_MAX_TOKENS=1000
LOG_LEVEL=INFO
LOG_FILE=/tmp/dashboard.log
```

## What to Keep

- **dashboard.py**: Kept for reference, but no longer used
- **README_DASHBOARD.md**: Kept for reference, superseded by README.md
- **.env**: Your existing environment variables work as before
- **credentials.json & token.pickle**: Google Calendar credentials unchanged
- **templates/**: Moved to `app/templates/`, but HTML content identical

## What to Delete (Optional)

After verifying everything works:

```bash
# Old files no longer needed:
rm dashboard.py
rm README_DASHBOARD.md
```

## Troubleshooting

### "Module not found" errors

Make sure you're using the virtual environment:
```bash
source .venv/bin/activate
python run.py
```

### Scripts don't work

Ensure they're executable:
```bash
chmod +x run.py scripts/*.sh
```

### Old process still running

Kill old dashboard processes:
```bash
pkill -f dashboard.py
pkill -f run.py
```

## Benefits of New Structure

### For Development

- **Easier Testing**: Each service can be tested independently
- **Clearer Code**: Find what you need quickly in organized modules
- **Better Error Messages**: Enhanced logging with emoji icons
- **Configuration Flexibility**: Change settings without editing code

### For Maintenance

- **Update One Service**: Modify Garmin integration without touching AI or Calendar code
- **Add Features**: Create new services in `app/services/` and register them
- **Debug Issues**: Check specific service logs and errors
- **Version Control**: .gitignore properly configured

### For Production

- **Environment Configs**: Switch between development/production easily
- **Security**: Sensitive data in .env (git-ignored by default)
- **Scalability**: Ready for additional features, database, authentication
- **Professional**: Follows industry-standard patterns

## Next Steps

1. Test the new structure: `python run.py`
2. Update keyboard shortcuts to use new script paths
3. Customize configuration in `.env`
4. Remove old `dashboard.py` once verified
5. Read new `README.md` for full documentation

## Questions?

Check:
- `README.md` for full documentation
- `/tmp/dashboard.log` for detailed logs
- `app/config.py` for all configuration options
