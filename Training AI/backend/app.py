"""Application entry point for the backend service.

Uses the factory defined in ``app/__init__.py`` so that blueprints and
configuration are centralised.  Keeps this file thin to simplify testing.
"""

# import the globally‑configured app instance from the package
from app import app, socketio
from scheduler import start_scheduler

# any route-specific logic that didn't belong in a blueprint can go here
# (the catch‑all index route is already defined in create_app)

if __name__ == '__main__':
    # Start background scheduler for automated reports
    start_scheduler()
    socketio.run(app, host='0.0.0.0', port=5000)
