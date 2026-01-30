#!/bin/bash

# Stop the Personal Dashboard

# Log execution
echo "$(date): Stop script executed" >> /tmp/dashboard_startup.log

if pgrep -f "run.py" > /dev/null; then
    pkill -9 -f "run.py"
    notify-send "Dashboard" "Server stopped" 2>/dev/null
    echo "$(date): Dashboard stopped" >> /tmp/dashboard_startup.log
else
    notify-send "Dashboard" "Not running" 2>/dev/null
    echo "$(date): Dashboard was not running" >> /tmp/dashboard_startup.log
fi
