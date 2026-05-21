#!/usr/bin/env python
"""
WSGI Application Entry Point for Gunicorn/Waitress
Production-ready application factory
"""
import sys
import os
import logging

# Set up path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'batuma_gprs_weather'))

# Set environment
os.environ.setdefault('ENVIRONMENT', 'production')
os.environ.setdefault('FLASK_DEBUG', 'False')

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Import the Flask app
from batuma_gprs_weather.app_simple import app

# Configure for production
app.config['ENV'] = 'production'
app.config['DEBUG'] = False
app.config['TESTING'] = False

# WSGI application instance
if __name__ == '__main__':
    # Direct execution (for testing)
    app.run()
else:
    # WSGI server execution (Gunicorn/Waitress)
    application = app
