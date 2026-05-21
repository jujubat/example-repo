#!/usr/bin/env python
"""Test server to verify port binding works on Windows"""

import sys
import os
import socket
import time

# Add batuma_gprs_weather directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'batuma_gprs_weather'))
os.chdir(os.path.join(os.path.dirname(__file__), 'batuma_gprs_weather'))

from app_simple import app

if __name__ == '__main__':
    print("=" * 60)
    print("BATUMA GPRS WEATHER - TEST SERVER")
    print("=" * 60)
    
    # Test port availability
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex(('127.0.0.1', 8000))
    if result == 0:
        print("[ERROR] Port 8000 is already in use!")
        sock.close()
        sys.exit(1)
    sock.close()
    
    print("[INFO] Port 8000 is available")
    print("[INFO] Starting Flask development server...")
    print("[INFO] URL: http://127.0.0.1:8000")
    print("[INFO] Ctrl+C to stop")
    print("-" * 60)
    print()
    
    # Use threaded=False to run single-threaded for debugging
    app.run(
        host='127.0.0.1',
        port=8000,
        debug=False,  # Disable debug mode to avoid reloader
        threaded=False,
        use_reloader=False  # Disable reloader which can cause issues
    )
