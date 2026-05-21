#!/usr/bin/env python
"""
Production WSGI Server using Waitress
Windows-friendly alternative to Gunicorn
Usage: python wsgi_waitress.py
"""
import os
import sys
import logging

# Set up path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Set environment
os.environ.setdefault('ENVIRONMENT', 'production')
os.environ.setdefault('FLASK_DEBUG', 'False')
os.environ.setdefault('FLASK_ENV', 'production')

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Import Waitress
try:
    from waitress import serve
except ImportError:
    logger.error("Waitress not installed. Run: pip install waitress")
    sys.exit(1)

# Import Flask app
from wsgi import application

if __name__ == '__main__':
    # Configuration
    host = os.getenv('WAITRESS_HOST', '0.0.0.0')
    port = int(os.getenv('WAITRESS_PORT', 8000))
    threads = int(os.getenv('WAITRESS_THREADS', 4))
    
    # Create logs directory
    os.makedirs('logs', exist_ok=True)
    
    # Print startup info
    print("[STARTUP] Batuma GPRS Weather - Waitress WSGI Server")
    print(f"[CONFIG] Host: {host}")
    print(f"[CONFIG] Port: {port}")
    print(f"[CONFIG] Threads: {threads}")
    print(f"[CONFIG] Environment: production")
    print("[LISTEN] Starting server...")
    print(f"[URL] http://{host}:{port}")
    
    try:
        # Start Waitress server
        serve(
            application,
            host=host,
            port=port,
            threads=threads,
            _quiet=False,
            _call_on_close=None
        )
    except KeyboardInterrupt:
        print("\n[SHUTDOWN] Server shutdown by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"[ERROR] Server failed: {str(e)}")
        sys.exit(1)
