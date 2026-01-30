# Graceful Error Handling & Setup Instructions

## Feature Overview

The dashboard now gracefully handles missing API configurations and displays helpful setup instructions directly in each widget instead of breaking or showing generic errors.

## What Changed

### 1. Service Layer Updates

**All services now return setup instructions when not configured:**

- **Weather Service**: Shows setup message when `WEATHER_API_KEY` is missing
- **Garmin Service**: Shows setup message when `GARMIN_EMAIL`/`GARMIN_PASSWORD` are missing
- **AI Service**: Shows setup message when `OPEN_WEB_UI_API_KEY` is missing
- **Calendar Service**: Logs helpful setup instructions when `credentials.json` is missing

### 2. Dashboard UI Updates

**Each widget now displays context-specific setup instructions:**

#### Weather Widget
```
⚠️ Weather API not configured.
Get a free API key from https://openweathermap.org/api
and add it to your .env file as WEATHER_API_KEY

Setup Steps:
1. Get a free API key from OpenWeatherMap
2. Add to .env file: WEATHER_API_KEY=your_key
3. Restart the dashboard
```

#### Garmin Fitness Widget
```
⚠️ Garmin not configured.
Add your GARMIN_EMAIL and GARMIN_PASSWORD to .env file.
This feature is optional.

Setup Steps (Optional):
1. Add to .env file:
   GARMIN_EMAIL=your_email
   GARMIN_PASSWORD=your_password
2. Restart the dashboard
```

#### Google Calendar Widget
```
⚠️ Google Calendar Not Configured

Setup Steps:
1. Visit Google Cloud Console
2. Create a project & enable Calendar API
3. Create OAuth 2.0 credentials (Desktop app)
4. Download as credentials.json to project root
5. Restart dashboard - browser will open for authentication
```

#### AI Suggestions
```
⚠️ AI Not Configured

To enable AI suggestions:
1. Get an API key from your Open Web UI instance
2. Add it to your .env file as OPEN_WEB_UI_API_KEY
3. Restart the dashboard

This feature is optional - other widgets will continue to work!
```

### 3. Visual Styling

Added `.setup-message` CSS class with:
- Warm gradient background (yellow/amber)
- Orange left border
- Clear, readable typography
- Clickable links to setup resources
- Emphasized important text

## Benefits

### For New Users
- **No Confusion**: Clear instructions instead of cryptic errors
- **Self-Service**: Users can set up features themselves without documentation hunting
- **Progressive Setup**: Can start using the dashboard with just one API key
- **Optional Features**: Clearly marked which features are optional

### For Existing Users
- **Troubleshooting**: If a service stops working, see exactly what's wrong
- **Maintenance**: Easy to identify which API keys need renewal
- **Migration**: When moving to a new system, clear reminders of what needs configuration

### For Developers
- **Better UX**: Users don't get frustrated with blank widgets
- **Reduced Support**: Self-explanatory setup reduces support requests
- **Graceful Degradation**: Dashboard remains functional even if some services fail

## How It Works

### 1. Service Detection
Each service checks for required configuration:

```python
# Weather Service
if not self.api_key:
    logger.warning("Weather API key not configured")
    return self._get_fallback_weather("Not configured")
```

### 2. Setup Messages
Services return structured data with setup information:

```python
return {
    "temperature": 15,  # Fallback value
    "setup_required": "Not configured",
    "setup_message": "⚠️ Weather API not configured. Get a free..."
}
```

### 3. Frontend Display
Dashboard checks for `setup_message` and displays instructions:

```javascript
if (quickData.weather.setup_message) {
    // Show setup instructions in widget
    document.getElementById('weather-section').innerHTML = `...setup HTML...`;
} else {
    // Show normal data
    document.getElementById('temperature').textContent = data.temperature;
}
```

## Example Scenarios

### Scenario 1: Complete Fresh Install
User clones repo, copies `.env.example` to `.env`, runs dashboard:
- ✅ Dashboard loads successfully
- ⚠️ All widgets show setup instructions
- 👤 User can configure one service at a time
- 🎯 Dashboard remains usable throughout setup

### Scenario 2: Partial Configuration
User has Weather API key but not Garmin:
- ✅ Weather widget shows live data
- ⚠️ Garmin widget shows "optional" setup instructions
- 👤 User can use weather features while deciding about Garmin
- 🎯 No errors, just clear options

### Scenario 3: Expired API Key
User's Weather API key expires:
- ⚠️ Weather widget automatically shows "API key invalid" message
- ✅ Other widgets continue working
- 📝 Message includes link to get new key
- 🎯 User knows exactly what to fix

## Technical Details

### Modified Files
- `app/services/weather_service.py` - Added setup messages
- `app/services/garmin_service.py` - Added setup messages
- `app/services/ai_service.py` - Added setup messages
- `app/services/calendar_service.py` - Added logging hints
- `app/routes/api.py` - Added setup_required flag
- `app/templates/dashboard.html` - Added UI handling + CSS

### API Response Structure
```json
{
  "weather": {
    "temperature": 15,
    "setup_required": "Not configured",
    "setup_message": "⚠️ Weather API not configured..."
  },
  "garmin": {
    "sleep_score": "Not configured",
    "setup_message": "⚠️ Garmin not configured..."
  },
  "calendar": {
    "today": [],
    "upcoming": [],
    "setup_required": true
  }
}
```

## Future Enhancements

Possible improvements:
- [ ] Interactive setup wizard
- [ ] Test API key directly from dashboard
- [ ] Setup progress indicator
- [ ] Email notification when API keys expire
- [ ] One-click API key renewal links

## Testing

To test setup messages:
1. Comment out API keys in `.env` file
2. Restart dashboard
3. Verify setup instructions appear
4. Click setup links to verify they work
5. Add API key back and verify widget returns to normal

## Documentation Updates

Updated documentation:
- ✅ SETUP.md - Mentions graceful degradation
- ✅ README.md - Explains optional features
- ✅ .env.example - Clear comments about optional vs required

---

**Result**: Dashboard is now much more user-friendly and accessible to new users while remaining robust for production use! 🎉
