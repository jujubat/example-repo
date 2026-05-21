# Batuma GPRS Weather - Production Server Setup

## 🚀 Quick Start

### Windows (Easiest)

```cmd
# Option 1: Waitress (Recommended for Windows)
start_waitress.bat

# Option 2: Gunicorn (Requires WSL or compatibility mode)
start_production.bat
```

**Server starts on:** `http://localhost:8000`

### Linux/macOS

```bash
# Activate virtual environment
source .venv/bin/activate

# Option 1: Gunicorn (Recommended)
gunicorn -c gunicorn_config.py wsgi:application

# Option 2: Waitress
python wsgi_waitress.py

# Option 3: Systemd service
sudo systemctl start batuma
sudo systemctl status batuma
```

**Server starts on:** `http://0.0.0.0:8000`

---

## 📋 Installation

### Prerequisites

- Python 3.13+
- pip / Virtual environment
- 1GB RAM minimum (2GB+ recommended)
- 100MB disk space

### Step 1: Clone Repository

```bash
git clone <repo-url> batuma_full_app
cd batuma_full_app
```

### Step 2: Create Virtual Environment

```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# Linux/macOS
python3 -m venv .venv
source .venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### Step 4: Configure Environment

```bash
# Create .env file (if needed)
export ENVIRONMENT=production
export FLASK_ENV=production
export FLASK_DEBUG=False

# API Keys (add to your environment)
export GOOGLE_MAPS_API_KEY=your_key_here
export WEATHER_API_KEY=your_key_here
export FIREBASE_CREDENTIALS=path/to/credentials.json
```

### Step 5: Create Logs Directory

```bash
mkdir -p logs
```

### Step 6: Start Server

**Windows:**
```cmd
start_waitress.bat
```

**Linux/macOS:**
```bash
gunicorn -c gunicorn_config.py wsgi:application
```

---

## 🔧 Configuration

### Environment Variables

| Variable | Default | Purpose |
|----------|---------|---------|
| `ENVIRONMENT` | `production` | Deployment environment |
| `FLASK_ENV` | `production` | Flask environment mode |
| `FLASK_DEBUG` | `False` | Enable debug mode |
| `GUNICORN_BIND` | `0.0.0.0:8000` | Bind address and port |
| `GUNICORN_WORKERS` | `(CPU×2)+1` | Number of worker processes |
| `GUNICORN_TIMEOUT` | `60` | Request timeout (seconds) |
| `WAITRESS_HOST` | `0.0.0.0` | Waitress host |
| `WAITRESS_PORT` | `8000` | Waitress port |
| `WAITRESS_THREADS` | `4` | Waitress thread pool |

### Gunicorn Configuration

Edit [gunicorn_config.py](gunicorn_config.py):

```python
# Worker count (for 4 CPUs: 9 workers)
workers = (multiprocessing.cpu_count() * 2) + 1

# Request timeout
timeout = 60

# Max requests before worker restart
max_requests = 1000

# Keep-alive timeout
keepalive = 5
```

### Waitress Configuration

Edit [wsgi_waitress.py](wsgi_waitress.py):

```python
# Thread pool size
threads = 4

# Host and port
host = os.getenv('WAITRESS_HOST', '0.0.0.0')
port = int(os.getenv('WAITRESS_PORT', 8000))

# Logging level
log_level = 'info'
```

---

## 📊 Testing

### Health Check

```bash
# Test server is running
curl http://localhost:8000/api/health

# Expected response:
# {"status": "healthy", "timestamp": "2026-01-17T16:54:00Z"}
```

### Test All Features

```bash
# 1. Weather API
curl -X POST http://localhost:8000/api/weather/by-place \
  -H "Content-Type: application/json" \
  -d '{"place": "New York"}'

# 2. Travel Time
curl -X POST http://localhost:8000/api/routes/travel-time \
  -H "Content-Type: application/json" \
  -d '{"start": "New York", "end": "Boston"}'

# 3. Transit Routes
curl http://localhost:8000/api/transit/routes

# 4. Frontend
open http://localhost:8000
```

### Load Testing

```bash
# Install Apache Bench
sudo apt install apache2-utils

# 1000 requests, 100 concurrent
ab -n 1000 -c 100 http://localhost:8000/api/health

# Install locust for advanced testing
pip install locust
locust -f locustfile.py --host=http://localhost:8000
```

---

## 🔒 Security

### Production Checklist

- [ ] HTTPS/SSL enabled
- [ ] Firewall configured (allow only :80 and :443)
- [ ] Non-root user running service
- [ ] Environment variables for secrets
- [ ] Rate limiting enabled
- [ ] Input validation active
- [ ] CORS properly configured
- [ ] Security headers set
- [ ] Logs not exposing sensitive data

### SSL/TLS Setup

```bash
# Generate self-signed certificate
openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -days 365

# With Gunicorn
gunicorn --certfile=cert.pem --keyfile=key.pem --bind 0.0.0.0:8443 wsgi:application

# With Nginx (recommended)
sudo cp cert.pem /etc/nginx/certs/
sudo cp key.pem /etc/nginx/certs/
sudo nginx -t && sudo systemctl restart nginx
```

---

## 📈 Scaling

### Single Server (100-500 users)
```bash
gunicorn -c gunicorn_config.py wsgi:application
```

### Multiple Instances (500-5000 users)
```bash
# Start 3 instances
gunicorn -b 127.0.0.1:8000 wsgi:application &
gunicorn -b 127.0.0.1:8001 wsgi:application &
gunicorn -b 127.0.0.1:8002 wsgi:application &

# Configure Nginx to load balance (see nginx.conf)
```

### Containerized (Docker - 5000+ users)
```bash
# Build image
docker build -t batuma:latest .

# Run container
docker run -d -p 8000:8000 \
  -e ENVIRONMENT=production \
  -v /opt/batuma/logs:/app/logs \
  batuma:latest

# Or with docker-compose
docker-compose up -d
```

---

## 🐳 Docker Deployment

### Build and Run

```bash
# Build
docker build -t batuma-gprs:latest .

# Run single container
docker run -d \
  --name batuma \
  -p 8000:8000 \
  -e ENVIRONMENT=production \
  -v batuma-logs:/app/logs \
  batuma-gprs:latest

# Run with docker-compose
docker-compose up -d
```

### Docker Compose Full Stack

```bash
# Start full stack (app + nginx + prometheus + grafana)
docker-compose up -d

# View logs
docker-compose logs -f batuma

# Stop services
docker-compose down

# Volumes
docker volume ls | grep batuma
docker volume inspect batuma_logs
```

**Access Points:**
- App: http://localhost:8000
- Nginx: http://localhost:80
- Prometheus: http://localhost:9090
- Grafana: http://localhost:3000 (admin/admin)

---

## 🔍 Monitoring

### Logs

**Real-time monitoring:**
```bash
# View error logs
tail -f logs/error.log

# View access logs
tail -f logs/access.log

# Search for errors
grep ERROR logs/error.log
grep 500 logs/access.log

# Count requests
wc -l logs/access.log
```

**Log Rotation (Linux):**
```bash
# /etc/logrotate.d/batuma
/opt/batuma_full_app/logs/*.log {
    daily
    missingok
    rotate 14
    compress
    delaycompress
    notifempty
    create 0640 www-data www-data
    sharedscripts
    postrotate
        systemctl reload batuma > /dev/null 2>&1 || true
    endscript
}
```

### Server Health

```bash
# CPU and Memory
top -p $(pgrep -f gunicorn | tr '\n' ',')

# Process count
ps aux | grep gunicorn | grep -v grep | wc -l

# Memory usage
ps aux | grep gunicorn | awk '{sum+=$6} END {print sum " KB"}'

# Port listening
netstat -tlnp | grep 8000

# Connections
netstat -an | grep ESTABLISHED | wc -l
```

### Prometheus Metrics

```bash
# Access Prometheus
curl http://localhost:9090

# Query examples
http_requests_total
process_resident_memory_bytes
gunicorn_workers

# Grafana dashboards
http://localhost:3000
```

---

## 🛠️ Troubleshooting

### Server Won't Start

**Error: "Address already in use"**
```bash
# Find process using port
lsof -i :8000
kill -9 <PID>

# Or wait 60 seconds for TIME_WAIT
sleep 60
```

**Error: "Module not found"**
```bash
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

**Error: "Permission denied"**
```bash
# Check directory permissions
ls -la /opt/batuma_full_app/
sudo chown -R www-data:www-data /opt/batuma_full_app/
```

### High Memory Usage

```bash
# Reduce workers
export GUNICORN_WORKERS=2

# Set max requests to recycle workers
gunicorn --max-requests 500 wsgi:application

# Monitor memory
watch -n 1 'ps aux | grep gunicorn | awk "{sum+=\$6} END {print sum \" KB\"}"'
```

### Slow Responses

```bash
# Check worker status
ps aux | grep gunicorn

# Monitor load average
uptime

# Check I/O wait
iostat -x 1 5

# Review error logs for timeout errors
grep "timeout" logs/error.log
```

### Connection Issues

```bash
# Check if server listening
netstat -tlnp | grep 8000

# Test connectivity
curl -v http://localhost:8000/api/health

# Check firewall
sudo ufw status
sudo ufw allow 8000
```

---

## 🚀 Advanced Topics

### Performance Tuning

```bash
# Increase worker connections
ulimit -n 65535

# TCP optimization (Linux)
sysctl -w net.core.somaxconn=32768
sysctl -w net.ipv4.tcp_max_syn_backlog=32768

# Gunicorn worker class
gunicorn --worker-class gevent wsgi:application  # Async
gunicorn --worker-class uvicorn.workers.UvicornWorker wsgi:application  # ASGI
```

### Database Connection Pooling

```python
# Already configured in app_simple.py
# SQLAlchemy connection pool:
# pool_size=10, max_overflow=20, pool_timeout=30
```

### API Rate Limiting

Already configured in Nginx config:
```nginx
limit_req_zone $binary_remote_addr zone=api_limit:10m rate=100r/s;
limit_req zone=api_limit burst=200 nodelay;
```

### Caching

```bash
# Redis caching (optional)
pip install redis

# Enable in app_simple.py
from flask_caching import Cache
cache = Cache(app, config={'CACHE_TYPE': 'redis'})
```

---

## 📞 Support

### Issue Categories

| Priority | Issue | Response Time | Contact |
|----------|-------|----------------|---------|
| P1 | Server down | 5 min | On-call |
| P2 | Features broken | 30 min | Team lead |
| P3 | Performance issues | 2 hours | Dev team |
| P4 | Documentation | Next sprint | Team |

### Debug Commands

```bash
# Full debug info
python -c "import sys; print(sys.version); import flask; print(flask.__version__)"

# Check imports
python -c "from batuma_gprs_weather import app_simple; print('OK')"

# Test API
python wsgi.py  # Direct WSGI app test
```

---

## 📚 Documentation

- [PRODUCTION_WSGI_SETUP.md](PRODUCTION_WSGI_SETUP.md) - Detailed setup guide
- [DEPLOYMENT_CHECKLIST.md](DEPLOYMENT_CHECKLIST.md) - Pre/post deployment checks
- [README.md](README.md) - Main documentation
- [gunicorn_config.py](gunicorn_config.py) - Gunicorn configuration
- [wsgi.py](wsgi.py) - WSGI entry point
- [nginx.conf](nginx.conf) - Nginx reverse proxy config
- [batuma.service](batuma.service) - Systemd service file

---

## 🎯 Next Steps

1. ✅ Install and test locally
2. ✅ Configure environment variables
3. ✅ Run production server
4. ✅ Setup monitoring
5. ✅ Configure SSL/TLS
6. ✅ Setup Nginx reverse proxy
7. ✅ Deploy to production server
8. ✅ Monitor logs and metrics
9. ✅ Setup automated backups
10. ✅ Plan disaster recovery

---

**Last Updated:** January 17, 2026  
**Version:** 1.0  
**Status:** ✅ Production Ready

For support or issues, refer to the troubleshooting section or contact the development team.
