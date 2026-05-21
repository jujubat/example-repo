#!/bin/bash

# Batuma GPRS Weather - Production WSGI Server Startup
# Uses Gunicorn on Linux/Mac, Waitress on Windows
# This is a production-grade server suitable for deployment
# Usage: bash start_production.sh

set -e

# Get the script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
APP_DIR="$SCRIPT_DIR/batuma_gprs_weather"

# Create logs directory if it doesn't exist
mkdir -p "$APP_DIR/logs"

# Set environment variables for production
export ENVIRONMENT=production
export FLASK_DEBUG=False
export WSGI_HOST=0.0.0.0
export WSGI_PORT=8000
export WSGI_WORKERS=4

echo ""
echo "====================================================="
echo "  Batuma GPRS Weather - Production WSGI Server"
echo "====================================================="
echo ""
echo "Environment: $ENVIRONMENT"
echo "Server: Gunicorn/Waitress WSGI"
echo "Bind: $WSGI_HOST:$WSGI_PORT"
echo "Workers: $WSGI_WORKERS"
echo ""

# Activate virtual environment if it exists
if [ -d ".venv" ]; then
    source .venv/bin/activate
    echo "✅ Virtual environment activated"
elif [ -d "venv" ]; then
    source venv/bin/activate
    echo "✅ Virtual environment activated"
fi

# Change to app directory
cd "$APP_DIR"

# Start production WSGI server
echo "Starting production WSGI server..."
echo ""

python wsgi_production.py

if [ $? -ne 0 ]; then
    echo ""
    echo "ERROR: Failed to start production server"
    echo "Make sure dependencies are installed: pip install gunicorn waitress"
    echo ""
    exit 1
fi
