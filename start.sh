#!/bin/bash

# Activate virtual environment
source venv/bin/activate

# Initialize database if needed
python init_db.py

# Start gunicorn
gunicorn --workers 3 --bind 0.0.0.0:5000 app:app 