# Production WSGI Deployment Checklist

## Pre-Deployment (Development)

### Code Preparation
- [ ] All features tested and working locally
- [ ] All 4 requested features implemented:
  - [ ] Weather fetching by location
  - [ ] Travel time calculation
  - [ ] Bus/Train routes with categories
  - [ ] Weather UI removed
- [ ] No console errors or warnings
- [ ] No debug output in logs
- [ ] Security: No hardcoded credentials or secrets

### Dependency Management
- [ ] requirements.txt updated with all production dependencies
- [ ] Version pinning: All packages have specific versions
- [ ] No development-only packages in requirements.txt
- [ ] Tested clean install: `pip install -r requirements.txt`

### Configuration Files
- [ ] `wsgi.py` created and tested
- [ ] `gunicorn_config.py` configured for production
- [ ] `wsgi_waitress.py` created (Windows fallback)
- [ ] Environment variables documented
- [ ] Secrets stored in environment, not in code

### Documentation
- [ ] `PRODUCTION_WSGI_SETUP.md` reviewed
- [ ] Deployment steps documented
- [ ] Troubleshooting guide available
- [ ] Team members trained on deployment process

---

## Staging Deployment

### Infrastructure Setup
- [ ] Staging server provisioned
- [ ] Python 3.13+ installed
- [ ] Virtual environment created: `python -m venv .venv`
- [ ] Firewall configured to allow port 8000
- [ ] Logs directory created: `mkdir -p logs`

### Application Deployment
- [ ] Code cloned/copied to staging server
- [ ] Dependencies installed: `pip install -r requirements.txt`
- [ ] Environment variables configured
- [ ] Database connectivity tested (Firestore, Google Maps, Weather API)
- [ ] WSGI server started successfully

### Testing in Staging
- [ ] [ ] Server responds to health check: `curl http://localhost:8000/api/health`
- [ ] [ ] All 4 features work in staging
- [ ] [ ] Weather API functional
- [ ] [ ] Travel time calculation accurate
- [ ] [ ] Transit routes display correctly
- [ ] [ ] Frontend loads without errors
- [ ] [ ] API response times acceptable (< 2 seconds)
- [ ] [ ] Load testing completed: 100+ concurrent users
- [ ] [ ] Error handling tested
- [ ] [ ] Logging captures errors properly

### Security Testing
- [ ] [ ] HTTPS/SSL working (if configured)
- [ ] [ ] Rate limiting functional
- [ ] [ ] Input validation working
- [ ] [ ] No exposed secrets in logs
- [ ] [ ] CORS headers correct
- [ ] [ ] Authentication/Authorization tested

---

## Production Deployment

### Pre-Production Checklist
- [ ] All staging tests passed
- [ ] Backup of current production taken
- [ ] Rollback plan documented
- [ ] Team notified of deployment window
- [ ] Monitoring alerts configured
- [ ] Log aggregation ready

### Production Infrastructure
- [ ] Production server ready
- [ ] Python 3.13+ installed
- [ ] Virtual environment created
- [ ] Firewall rules configured
- [ ] SSL certificates installed (if using HTTPS)
- [ ] Logs directory with proper permissions
- [ ] Backup location configured

### Production Deployment Steps

1. **Clone/Copy Application**
   ```bash
   cd /opt/batuma_full_app
   git clone ... .
   # OR copy files from staging
   ```

2. **Setup Virtual Environment**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. **Install Dependencies**
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

4. **Configure Environment**
   ```bash
   export ENVIRONMENT=production
   export FLASK_ENV=production
   export FLASK_DEBUG=False
   export GUNICORN_WORKERS=4
   export GUNICORN_BIND=0.0.0.0:8000
   # Add other environment variables
   ```

5. **Create Required Directories**
   ```bash
   mkdir -p logs
   chmod 755 logs
   ```

6. **Test WSGI Server Locally**
   ```bash
   gunicorn -c gunicorn_config.py wsgi:application
   # OR
   python wsgi_waitress.py
   ```

7. **Setup Reverse Proxy (Nginx)**
   ```bash
   sudo cp nginx.conf /etc/nginx/sites-available/batuma
   sudo ln -s /etc/nginx/sites-available/batuma /etc/nginx/sites-enabled/
   sudo nginx -t
   sudo systemctl restart nginx
   ```

8. **Setup Systemd Service (Linux)**
   ```bash
   sudo cp batuma.service /etc/systemd/system/
   sudo systemctl daemon-reload
   sudo systemctl enable batuma
   sudo systemctl start batuma
   ```

9. **Verify Production Deployment**
   - [ ] Server starts without errors
   - [ ] Health check passes: `curl http://localhost:8000/api/health`
   - [ ] All features working
   - [ ] Logs being written correctly
   - [ ] Response times acceptable
   - [ ] No error messages in logs

### Post-Deployment Verification

- [ ] **Health Monitoring**
  ```bash
  curl https://production.batuma.local/api/health
  ```

- [ ] **Feature Testing**
  - [ ] Weather endpoint responds
  - [ ] Travel time calculation works
  - [ ] Transit routes display
  - [ ] Frontend loads correctly

- [ ] **Performance Monitoring**
  - [ ] Average response time < 500ms
  - [ ] CPU usage < 80%
  - [ ] Memory usage stable
  - [ ] No memory leaks (check after 1 hour)

- [ ] **Error Monitoring**
  - [ ] No critical errors in logs
  - [ ] No 500 errors in access logs
  - [ ] All API endpoints responding

- [ ] **Security Verification**
  - [ ] HTTPS enabled and working
  - [ ] Rate limiting active
  - [ ] No sensitive data in logs
  - [ ] Security headers present

---

## Scaling & Load Balancing

### Multi-Instance Setup

If expecting > 100 concurrent users:

1. **Run Multiple Gunicorn Instances**
   ```bash
   # Instance 1
   gunicorn -c gunicorn_config.py -b 127.0.0.1:8000 wsgi:application &
   
   # Instance 2
   gunicorn -c gunicorn_config.py -b 127.0.0.1:8001 wsgi:application &
   
   # Instance 3
   gunicorn -c gunicorn_config.py -b 127.0.0.1:8002 wsgi:application &
   ```

2. **Configure Nginx Load Balancing** (already in nginx.conf)
   - Upstream servers defined
   - Least connections algorithm
   - Health checks enabled

3. **Monitor Each Instance**
   ```bash
   ps aux | grep gunicorn
   tail -f logs/error.log
   ```

---

## Monitoring & Maintenance

### Daily Checks
- [ ] Server running: `systemctl status batuma`
- [ ] No errors in logs: `tail -20 logs/error.log`
- [ ] Response times normal: Check nginx access logs
- [ ] CPU/Memory usage normal: `top -p $(pgrep -f gunicorn | tr '\n' ',')`

### Weekly Checks
- [ ] Review error logs for patterns
- [ ] Verify backup schedule
- [ ] Check disk space: `df -h`
- [ ] Test manual restart: `systemctl restart batuma`

### Monthly Checks
- [ ] Review performance metrics
- [ ] Update security patches
- [ ] Verify disaster recovery procedures
- [ ] Load testing simulation
- [ ] Security audit

### Quarterly Checks
- [ ] Full system performance review
- [ ] Dependency updates assessment
- [ ] Capacity planning
- [ ] Security penetration testing
- [ ] Disaster recovery drill

---

## Rollback Plan

If issues occur post-deployment:

### Immediate Actions (First 5 minutes)
```bash
# 1. Check status
systemctl status batuma

# 2. Check recent logs
tail -50 logs/error.log

# 3. If service crashed, restart
systemctl restart batuma

# 4. If restart fails, stop service
systemctl stop batuma
```

### Quick Rollback (Within 30 minutes)
```bash
# 1. Restore previous application version
git checkout <previous-commit>
# OR
cp -r backup/batuma_gprs_weather/* batuma_gprs_weather/

# 2. Reinstall dependencies
pip install -r requirements.txt

# 3. Restart service
systemctl restart batuma

# 4. Verify health
curl https://batuma.local/api/health
```

### Full Rollback (If quick rollback fails)
```bash
# 1. Stop production service
systemctl stop batuma

# 2. Restore from backup
restore_database_backup.sh

# 3. Start previous version
systemctl start batuma

# 4. Notify team
# Send notification to team chat/email
```

---

## Support & Escalation

### Issue Categories

**P1 - Critical (Server Down)**
- [ ] No response from health endpoint
- [ ] Cannot connect to server
- **Response Time:** 5 minutes
- **Contact:** On-call engineer

**P2 - Major (Features Broken)**
- [ ] Core features not working
- [ ] API errors 500+
- **Response Time:** 30 minutes
- **Contact:** Development team lead

**P3 - Minor (Performance/UX)**
- [ ] Slow response times
- [ ] UI glitches
- **Response Time:** 2-4 hours
- **Contact:** Development team

**P4 - Documentation**
- [ ] Documentation issues
- [ ] Process improvements
- **Response Time:** Next sprint
- **Contact:** Team lead

---

## Deployment History

| Date | Version | Deployed By | Status | Notes |
|------|---------|------------|--------|-------|
| 2026-01-17 | 1.0 | TBD | Pending | Initial production deployment |
| | | | | |

---

## Quick Reference Commands

```bash
# Check service status
systemctl status batuma

# View logs in real-time
journalctl -u batuma -f

# Restart service
systemctl restart batuma

# Stop service
systemctl stop batuma

# Start service
systemctl start batuma

# View Nginx status
systemctl status nginx

# Test Nginx configuration
nginx -t

# Reload Nginx (without downtime)
nginx -s reload

# Monitor server resources
top -p $(pgrep -f gunicorn | tr '\n' ',')

# Check disk space
df -h

# View memory usage
free -h

# Connections to port 8000
netstat -tlnp | grep 8000
lsof -i :8000
```

---

**Last Updated:** January 17, 2026  
**Version:** 1.0  
**Status:** Ready for Production
