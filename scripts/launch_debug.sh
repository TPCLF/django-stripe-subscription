#!/bin/bash

# Configuration
PROJECT_PATH="/home/user/django-stripe-subscription"
LOG="$HOME/.local/share/applications/scripts/launcher_browser_debug.log"
exec > >(tee -a "$LOG") 2>&1

# Logging start
echo "[`date`] Launcher started"

# Launch Terminal with Tabs
# 1. Django Server
# 2. Stripe CLI Listener
gnome-terminal --window \
  --tab --title="Django Server" -- bash -c "cd $PROJECT_PATH; source .venv/bin/activate; python manage.py runserver 8000; exec bash" \
  --tab --title="Stripe Listener" -- bash -c "cd $PROJECT_PATH; stripe listen --forward-to localhost:8000/stripe/webhook/; exec bash" \
  --tab --title="Terminal" -- bash -c "cd $PROJECT_PATH; ls -F; exec bash"

echo "Launcher finished. Press Enter to close this status window."
read

# Wait for server to potentially spin up
sleep 2

# Open Browser
xdg-open "http://localhost:8000" >> "$LOG" 2>&1

exit 0
