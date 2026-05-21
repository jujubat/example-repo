# Production WSGI Server Setup Guide

## Overview

This guide covers setting up Batuma GPRS Weather with production-grade WSGI servers on Windows, Linux, and macOS.

### Supported WSGI Servers

1. **Gunicorn** - Production-ready, Unix/Linux/macOS preferred
2. **Waitress** - Windows-friendly, pure Python WSGI server
3. **uWSGI** - Advanced features, higher performance

---

## Quick Start

### Option 1: Gunicorn (Linux/macOS/Windows with WSL)

```bash
# Install dependencies (already in requirements.txt)
pip install gunicorn

# Start server
cd /path/to/Batuma_full_app
gunicorn -c gunicorn_config.py wsgi:application
```

**Or on Windows:**
```cmd
start_production.bat
```

### Option 2: Waitress (Windows-Friendly)

```bash
# Install Waitress
pip install waitress

# Start server
python wsgi_waitress.py
```

**Or on Windows with batch file:**
```cmd
start_waitress.bat
```

---

## Detailed Setup

### 1. Directory Structure

```
Batuma_full_app/
├── wsgi.py                          # WSGI entry point
├── gunicorn_config.py               # Gunicorn configuration
├── wsgi_waitress.py                 # Waitress server script
├── start_production.bat              # Windows Gunicorn launcher
├── start_waitress.bat                # Windows Waitress launcher
├── .venv/                           # Python virtual environment
├── logs/                            # Server logs
│   ├── access.log                   # HTTP access logs
│   ├── error.log                    # Server error logs
│   └── gunicorn.pid                 # Process ID file
└── batuma_gprs_weather/             # Application code
    └── app_simple.py
```

### 2. Environment Variables

Set these for production:

```bash
# Core Settings
ENVIRONMENT=production
FLASK_ENV=production
FLASK_DEBUG=False

# Gunicorn Settings
GUNICORN_BIND=0.0.0.0:8000
GUNICORN_WORKERS=4
GUNICORN_ACCESS_LOG=logs/access.log
GUNICORN_ERROR_LOG=logs/error.log
GUNICORN_LOG_LEVEL=info

# Waitress Settings
WAITRESS_HOST=0.0.0.0
WAITRESS_PORT=8000
WAITRESS_THREADS=4
```

### 3. Configuration Files

#### gunicorn_config.py

Key settings:
- **Workers**: CPU_COUNT * 2 + 1 (auto-calculated)
- **Timeout**: 60 seconds
- **Max Requests**: 1000 (recycle worker processes)
- **Logging**: Access and error logs to files
- **Bind**: 0.0.0.0:8000 (all interfaces)

---

## Installation & Deployment

### Windows Installation

1. **Create Virtual Environment**
```cmd
python -m venv .venv
.venv\Scripts\activate
```

2. **Install Dependencies**
```cmd
pip install -r requirements.txt
```

3. **Create Logs Directory**
```cmd
mkdir logs
```

4. **Start Server**
```cmd
REM Option A: Gunicorn (WSL or Unix-like environment)
start_production.bat

REM Option B: Waitress (Pure Python, most compatible)
python wsgi_waitress.py
```

### Linux/macOS Installation

1. **Create Virtual Environment**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

2. **Install Dependencies**
```bash
pip install -r requirements.txt
```

3. **Create Logs Directory**
```bash
mkdir -p logs
```

4. **Start Server with Gunicorn**
```bash
gunicorn -c gunicorn_config.py wsgi:application
```

**Or with systemd service file:**
```bash
sudo systemctl start batuma
sudo systemctl enable batuma
```

---

## Systemd Service Setup (Linux)

Create `/etc/systemd/system/batuma.service`:

```ini
[Unit]
Description=Batuma GPRS Weather Service
After=network.target

[Service]
Type=notify
User=www-data
Group=www-data
WorkingDirectory=/opt/batuma_full_app
Environment="PATH=/opt/batuma_full_app/.venv/bin"
ExecStart=/opt/batuma_full_app/.venv/bin/gunicorn \
    -c gunicorn_config.py \
    -b 0.0.0.0:8000 \
    --workers 4 \
    --worker-class sync \
    --timeout 60 \
    wsgi:application
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable batuma
sudo systemctl start batuma
sudo systemctl status batuma
```

---

## Nginx Reverse Proxy Setup

### Nginx Configuration

Create `/etc/nginx/sites-available/batuma`:

```nginx
upstream batuma_app {
    server 127.0.0.1:8000;
    server 127.0.0.1:8001;
    server 127.0.0.1:8002;
}

server {
    listen 80;
    listen [::]:80;
    server_name batuma.local;

    client_max_body_size 10M;

    # Logging
    access_log /var/log/nginx/batuma_access.log;
    error_log /var/log/nginx/batuma_error.log;

    # Proxy settings
    location / {
        proxy_pass http://batuma_app;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_redirect off;
        proxy_buffering off;
        proxy_request_buffering off;
    }

    # Cache static files
    location ~* \.(jpg|jpeg|png|gif|ico|css|js)$ {
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
}
```

Enable:
```bash
sudo ln -s /etc/nginx/sites-available/batuma /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

---

## Load Balancing with Multiple Workers

### Running Multiple Gunicorn Instances

```bash
# Instance 1 (port 8000)
gunicorn -c gunicorn_config.py -b 127.0.0.1:8000 wsgi:application

# Instance 2 (port 8001)
gunicorn -c gunicorn_config.py -b 127.0.0.1:8001 wsgi:application

# Instance 3 (port 8002)
gunicorn -c gunicorn_config.py -b 127.0.0.1:8002 wsgi:application
```

Then configure Nginx to load balance across all three.

---

## Monitoring & Logging

### Access Logs

Located in `logs/access.log`:
```
127.0.0.1 - - [17/Jan/2026 16:54:00] "GET /api/health HTTP/1.1" 200 42 "-" "curl/7.68.0"
```

### Error Logs

Located in `logs/error.log`:
```
2026-01-17 16:54:00,123 - alerts.alert_engine - ERROR - Failed to fetch weather
```

### Monitor Server Health

```bash
# Check process
ps aux | grep gunicorn

# Check logs in real-time
tail -f logs/error.log
tail -f logs/access.log

# Monitor resources
top -p $(pgrep -f gunicorn | tr '\n' ',')

# Test health endpoint
curl http://localhost:8000/api/health
```

---

## Performance Tuning

### Worker Count Calculation

```python
workers = (CPU_COUNT * 2) + 1
# Example: 4 CPU cores = (4 * 2) + 1 = 9 workers
```

### Timeout Settings

```python
timeout = 60          # Request timeout (seconds)
keepalive = 5         # Keep-alive timeout (seconds)
max_requests = 1000   # Requests before worker recycles
```

### Waitress Thread Settings

```python
threads = 4           # Thread pool size
queue_size = 64       # Request queue depth
channel_timeout = 120 # Channel timeout
log_level = 'info'    # Logging level
```

---

## SSL/TLS Configuration

### Gunicorn with SSL

```bash
gunicorn \
  --certfile=/path/to/cert.pem \
  --keyfile=/path/to/key.pem \
  --ssl-version=TLSv1_2 \
  -b 0.0.0.0:8443 \
  wsgi:application
```

### Nginx with SSL

```nginx
server {
    listen 443 ssl http2;
    listen [::]:443 ssl http2;
    server_name batuma.local;

    ssl_certificate /etc/ssl/certs/batuma.crt;
    ssl_certificate_key /etc/ssl/private/batuma.key;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;

    # Redirect HTTP to HTTPS
    error_page 497 =301 https://$server_name$request_uri;
}
```

---

## Troubleshooting

### Server Won't Start

**Error: Port already in use**
```bash
# Find process using port 8000
lsof -i :8000
# Kill process
kill -9 <PID>
```

**Error: Address already in use**
```bash
# Wait a minute for TIME_WAIT to clear, or use SO_REUSEADDR
gunicorn --bind 0.0.0.0:8000 wsgi:application
```

### High Memory Usage

```bash
# Reduce workers
gunicorn -w 2 wsgi:application

# Set max_requests to recycle workers
gunicorn --max-requests 500 wsgi:application
```

### Slow Response Times

```bash
# Monitor worker processes
ps aux | grep gunicorn

# Check if workers are blocked
top

# Increase timeout
gunicorn --timeout 120 wsgi:application
```

### Connection Refused

```bash
# Check if server is listening
netstat -tlnp | grep 8000

# Verify binding
curl http://127.0.0.1:8000/api/health
curl http://0.0.0.0:8000/api/health    # Won't work, use 127.0.0.1
```

---

## Backup & Recovery

### Backup Configuration

```bash
# Backup production config
cp gunicorn_config.py gunicorn_config.py.backup
cp wsgi.py wsgi.py.backup

# Backup logs
tar -czf logs_backup.tar.gz logs/
```

### Graceful Restart

```bash
# Reload workers without dropping connections
kill -HUP $(cat logs/gunicorn.pid)

# Or with systemd
sudo systemctl reload batuma
```

---

## Performance Benchmarking

```bash
# Install Apache Bench
sudo apt install apache2-utils

# Benchmark
ab -n 1000 -c 10 http://localhost:8000/api/health

# With locust
pip install locust
locust -f locustfile.py --host=http://localhost:8000
```

---

## Security Considerations

1. ✅ Run as non-root user
2. ✅ Use firewall to restrict port access
3. ✅ Enable HTTPS/TLS
4. ✅ Use environment variables for secrets
5. ✅ Keep dependencies updated
6. ✅ Monitor logs for suspicious activity
7. ✅ Set up rate limiting
8. ✅ Use strong authentication

---

## Next Steps

1. Test production server locally
2. Deploy to staging environment
3. Load test and benchmark
4. Set up monitoring (Prometheus, NewRelic, etc.)
5. Configure log aggregation
6. Set up automated backups
7. Plan disaster recovery

---

**Last Updated:** January 17, 2026  
**Status:** Production Ready
