#!/bin/bash

# Personal Dashboard Startup Script
# This script starts the Flask server and opens the dashboard in your browser

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
cd "$PROJECT_DIR"

# Log execution for debugging
echo "$(date): Script executed" >> /tmp/dashboard_startup.log

# Determine Python executable (use venv if exists)
if [ -d "$PROJECT_DIR/.venv" ]; then
    PYTHON_BIN="$PROJECT_DIR/.venv/bin/python3"
    echo "$(date): Using virtual environment python" >> /tmp/dashboard_startup.log
elif [ -d "$PROJECT_DIR/venv" ]; then
    PYTHON_BIN="$PROJECT_DIR/venv/bin/python3"
    echo "$(date): Using virtual environment python" >> /tmp/dashboard_startup.log
else
    PYTHON_BIN="python3"
    echo "$(date): Using system python" >> /tmp/dashboard_startup.log
fi

# Check if dashboard is already running (check both old and new)
if pgrep -f "run.py" > /dev/null || pgrep -f "dashboard.py" > /dev/null; then
    # Kill old process if running
    pkill -f "dashboard.py" 2>/dev/null
    
    if pgrep -f "run.py" > /dev/null; then
        notify-send "Dashboard" "Already running - opening browser" 2>/dev/null
        # Just open the browser
        xdg-open http://localhost:5000 2>/dev/null || \
        firefox http://localhost:5000 2>/dev/null || \
        google-chrome http://localhost:5000 2>/dev/null
        exit 0
    fi
fi

# Start the dashboard in the background
notify-send "Dashboard" "Starting server..." 2>/dev/null
nohup "$PYTHON_BIN" "$PROJECT_DIR/run.py" > /tmp/dashboard.log 2>&1 &
DASHBOARD_PID=$!

# Wait for server to start (max 10 seconds)
for i in {1..20}; do
    if curl -s http://localhost:5000 > /dev/null 2>&1; then
        notify-send "Dashboard" "Server ready!" 2>/dev/null
        break
    fi
    sleep 0.5
done

# Open browser
xdg-open http://localhost:5000 2>/dev/null || \
firefox http://localhost:5000 2>/dev/null || \
google-chrome http://localhost:5000 2>/dev/null

notify-send "Dashboard" "Started successfully (PID: $DASHBOARD_PID)" 2>/dev/null
echo "$(date): Dashboard started with PID $DASHBOARD_PID" >> /tmp/dashboard_startup.log

echo "Dashboard started with PID $DASHBOARD_PID"
echo "Access at: http://localhost:5000"
echo "To stop: $PROJECT_DIR/scripts/stop_dashboard.sh"
