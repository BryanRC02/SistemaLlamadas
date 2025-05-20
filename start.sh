#!/bin/bash

# Activate virtual environment
source venv/bin/activate

# Initialize database if needed
python init_db.py

# Ensure log directory exists
mkdir -p /var/log/sistemallamadas

# Start gunicorn with proper configuration
gunicorn --workers 4 \
    --timeout 60 \
    --access-logfile /var/log/sistemallamadas/access.log \
    --error-logfile /var/log/sistemallamadas/error.log \
    --bind 0.0.0.0:5000 \
    "app:create_app()" 