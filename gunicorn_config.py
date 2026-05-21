# Gunicorn Production Configuration
# Usage: gunicorn -c gunicorn_config.py wsgi:application

import multiprocessing
import os

# Server Socket
bind = os.getenv('GUNICORN_BIND', '0.0.0.0:8000')
backlog = 2048

# Worker Processes
workers = int(os.getenv('GUNICORN_WORKERS', multiprocessing.cpu_count() * 2 + 1))
worker_class = 'sync'
worker_connections = 1000
timeout = 60
keepalive = 5

# Server Mechanics
daemon = False
pidfile = os.getenv('GUNICORN_PID_FILE', 'logs/gunicorn.pid')
umask = 0
user = None
group = None
tmp_upload_dir = None

# Logging
accesslog = os.getenv('GUNICORN_ACCESS_LOG', 'logs/access.log')
errorlog = os.getenv('GUNICORN_ERROR_LOG', 'logs/error.log')
loglevel = os.getenv('GUNICORN_LOG_LEVEL', 'info')
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# Process Naming
proc_name = 'batuma_gprs_weather'

# SSL (if needed - configure for production)
# keyfile = '/path/to/keyfile.key'
# certfile = '/path/to/certfile.crt'
# ssl_version = 'TLSv1_2'
# ciphers = 'HIGH:!aNULL:!MD5'
# ca_certs = '/path/to/ca.pem'

# Application
max_requests = 1000
max_requests_jitter = 50
reload_extra_files = []
reload = False
preload_app = False

# Environment
env = {
    'ENVIRONMENT': 'production',
    'FLASK_DEBUG': 'False',
    'FLASK_ENV': 'production'
}

# Hooks
def on_starting(server):
    print("[STARTUP] Batuma GPRS Weather WSGI server starting...")
    # Create logs directory if it doesn't exist
    os.makedirs('logs', exist_ok=True)

def when_ready(server):
    print(f"[READY] Server is ready. Spawned {server.cfg.workers} workers")
    print(f"[LISTEN] Listening on {server.cfg.bind}")
    print(f"[CONFIG] Environment: production")
    print(f"[CONFIG] Worker class: {server.cfg.worker_class}")

def on_exit(server):
    print("[SHUTDOWN] Shutting down Batuma GPRS Weather server")

def post_worker_init(worker):
    worker.log.info("[WORKER] Worker spawned (pid: %s)", worker.pid)

    print("✅ Server shutdown complete")
