# Error Handling & Service Resilience Guide

## Overview

This application is designed with fault-tolerant architecture so that if one service/module fails, others continue to work perfectly. This document explains how error handling and service resilience are implemented.

---

## Service Health Tracking

### Global Service Status

All services are tracked via a `service_status` dictionary in the main application:

```python
service_status = {
    'user_manager': False,           # User authentication service
    'alert_engine': False,           # Weather alerts and notifications
    'geocode': False,                # Address-to-coordinates conversion
    'google_routes': False,          # Google Maps routes API
}
```

### Status Values
- **`True`** - Service initialized successfully and ready to use
- **`False`** - Service failed to initialize or is unavailable

---

## Service Initialization with Error Handling

### Pattern: Try-Catch Initialization

Each service is wrapped in a try-catch block to prevent cascading failures:

```python
try:
    from alerts.alert_engine import AlertEngine
    alert_engine = AlertEngine()
    service_status['alert_engine'] = True
    logger.info("Alert Engine initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize Alert Engine: {str(e)}")
    alert_engine = None
    service_status['alert_engine'] = False
```

**Benefits:**
- ✅ Server starts even if a service fails
- ✅ Failed service doesn't crash the app
- ✅ Errors are logged for debugging
- ✅ Graceful degradation

---

## Endpoint-Level Error Handling

### 1. Service Availability Check

All endpoints check if required services are available:

```python
@app.route('/api/weather/by-place', methods=['POST'])
def get_weather_by_place():
    try:
        # Check if alert engine is available BEFORE using it
        if not service_status['alert_engine']:
            return jsonify({
                'success': False, 
                'error': 'Weather service temporarily unavailable',
                'service_status': service_status
            }), 503
        
        # Use service safely
        weather_data = alert_engine.get_weather(lat, lon)
        ...
```

**HTTP Status Codes Used:**
- **200** - Success
- **400** - Bad request (invalid input)
- **401** - Unauthorized (auth failed)
- **403** - Forbidden (insufficient permissions)
- **404** - Not found (location, resource not found)
- **500** - Internal server error (unexpected error)
- **503** - Service unavailable (dependent service is down)

### 2. Weather API Error Handling

```python
@app.route('/api/weather/by-place', methods=['POST'])
def get_weather_by_place():
    try:
        # Check service availability
        if not service_status['alert_engine']:
            return jsonify({...}), 503
        
        if not service_status['geocode']:
            return jsonify({...}), 503
        
        # Geocode address
        lat, lon = geocode_address(address)
        if lat is None or lon is None:
            return jsonify({...}), 404  # Location not found
        
        # Get weather
        weather_data = alert_engine.get_weather(lat, lon)
        if not weather_data:
            return jsonify({...}), 500
        
        return jsonify({'success': True, **weather_data}), 200
        
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500
```

### 3. Routes API Error Handling

```python
@app.route('/api/routes/travel-time', methods=['POST'])
def calculate_travel_time():
    try:
        # Check service availability
        if not service_status['google_routes']:
            return jsonify({
                'success': False,
                'error': 'Routes service temporarily unavailable',
                'service_status': service_status
            }), 503
        
        # Validate input
        if not 'start' in data or not 'end' in data:
            return jsonify({...}), 400
        
        # Calculate routes
        route = routes_api._get_single_route(start_location, end_location)
        if not route:
            return jsonify({...}), 500
        
        return jsonify({'success': True, 'route': {...}}), 200
        
    except ValueError as e:
        return jsonify({'success': False, 'error': f'Invalid value: {str(e)}'}), 400
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500
```

---

## Health Check Endpoints

### Main Application Health

**Endpoint:** `GET /api/health`

**Response (All Services Healthy):**
```json
{
    "status": "healthy",
    "timestamp": "2026-01-17T18:00:00",
    "service": "Tap Trip Auth & Admin API",
    "services": {
        "user_manager": true,
        "alert_engine": true,
        "geocode": true,
        "google_routes": true
    }
}
```

**Response (Weather Service Down):**
```json
{
    "status": "healthy",
    "timestamp": "2026-01-17T18:00:00",
    "service": "Tap Trip Auth & Admin API",
    "services": {
        "user_manager": true,
        "alert_engine": false,
        "geocode": true,
        "google_routes": true
    }
}
```

### Transit API Health

**Endpoint:** `GET /api/transit/health`

**Response:**
```json
{
    "status": "healthy",
    "service": "Transit API",
    "services": {
        "firestore_db": true,
        "transit_db": true,
        "route_manager": true
    }
}
```

---

## Error Response Format

All error responses follow a consistent format:

```json
{
    "success": false,
    "error": "Human-readable error message",
    "service_status": {
        "user_manager": true,
        "alert_engine": false,
        "geocode": true,
        "google_routes": true
    }
}
```

This allows clients to:
- ✅ Understand what went wrong
- ✅ See which services are down
- ✅ Retry with alternative services
- ✅ Provide user-friendly feedback

---

## Service Dependencies & Fallback Strategies

### Weather Service
**Dependencies:** Alert Engine, Geocoding
**If Weather Service Down:**
- ✅ Routes still work
- ✅ Authentication still works
- ✅ Transit system still works
- ❌ Weather endpoints return 503

### Routes Service
**Dependencies:** Google Routes API, Geocoding
**If Routes Service Down:**
- ✅ Weather still works
- ✅ Authentication still works
- ✅ Transit system still works
- ❌ Route endpoints return 503

### Transit Service
**Dependencies:** Firestore DB, Transit Manager
**If Transit Service Down:**
- ✅ Weather still works
- ✅ Routes still works
- ✅ Authentication still works
- ❌ Transit endpoints return 503

### Authentication Service
**Dependencies:** User Manager
**If Auth Service Down:**
- ❌ User login fails (503)
- ✅ Public endpoints work (no auth required)
- ✅ Health check works

---

## Global Error Handlers

### 404 Not Found
```python
@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'success': False,
        'error': 'Endpoint not found',
        'path': request.path,
        'service_status': service_status
    }), 404
```

### 500 Internal Server Error
```python
@app.errorhandler(500)
def internal_error(error):
    logger.error(f"500 Error: {str(error)}")
    return jsonify({
        'success': False,
        'error': 'Internal server error',
        'message': 'An unexpected error occurred. Please try again later.',
        'service_status': service_status
    }), 500
```

### 503 Service Unavailable
```python
@app.errorhandler(503)
def service_unavailable(error):
    logger.error(f"503 Error: {str(error)}")
    return jsonify({
        'success': False,
        'error': 'Service temporarily unavailable',
        'service_status': service_status
    }), 503
```

---

## Logging & Monitoring

### Log Levels

| Level | Use Case | Example |
|-------|----------|---------|
| INFO | Service initialized | "User Manager initialized successfully" |
| WARNING | Degraded functionality | "Service not initialized - Firestore unavailable" |
| ERROR | Service failure | "Failed to initialize Alert Engine: API key missing" |
| CRITICAL | Complete system failure | "All services failed to initialize" |

### Accessing Logs

```bash
# View error logs in real-time
tail -f logs/error.log

# View all application logs
tail -f logs/app.log

# Search for specific service errors
grep "Alert Engine" logs/error.log
```

---

## Client Behavior Recommendations

### Check Service Status

```javascript
// Check which services are available
async function checkServiceStatus() {
    const response = await fetch('http://localhost:8000/api/health');
    const data = await response.json();
    
    console.log('Services:', data.services);
    
    if (!data.services.alert_engine) {
        console.warn('Weather service is down');
    }
}
```

### Retry Logic

```javascript
async function callEndpointWithRetry(endpoint, maxRetries = 3) {
    let retries = 0;
    
    while (retries < maxRetries) {
        try {
            const response = await fetch(endpoint);
            
            if (response.status === 503) {
                // Service unavailable - wait and retry
                await new Promise(r => setTimeout(r, 1000 * (retries + 1)));
                retries++;
                continue;
            }
            
            return response;
        } catch (e) {
            console.error('Request failed:', e);
            retries++;
        }
    }
    
    throw new Error('Max retries exceeded');
}
```

### Graceful Degradation in UI

```javascript
// Show appropriate message based on service status
function displayWeatherOrAlternative(data) {
    if (!data.services.alert_engine) {
        showPlaceholder('Weather service currently unavailable. Please try again later.');
        return;
    }
    
    if (data.weather) {
        displayWeather(data.weather);
    } else {
        showPlaceholder('Could not retrieve weather data');
    }
}
```

---

## Testing Service Resilience

### Simulate Service Failure

To test that other services continue working when one fails:

```python
# Temporarily disable a service for testing
service_status['alert_engine'] = False

# Test that weather endpoints return 503
# GET /api/weather/by-place
# Expected: 503 Service Unavailable

# Test that other endpoints still work
# GET /api/health
# Expected: 200 OK (showing alert_engine as False)
```

### Load Testing with Service Degradation

```bash
# Run load test while a service is down
locust -f locustfile.py --host=http://localhost:8000

# Monitor that requests are still handled (even if some fail)
# Overall uptime should remain high
```

---

## Troubleshooting Guide

### Common Issues & Solutions

| Issue | Cause | Solution |
|-------|-------|----------|
| "Weather service unavailable" (503) | Alert Engine initialization failed | Check API keys, restart app |
| "Routes service unavailable" (503) | Google Routes API not responding | Check internet, API quota |
| "Geocoding service unavailable" (503) | Geocoding module import failed | Check geocode.py syntax |
| "Auth service unavailable" (503) | User Manager initialization failed | Check database connection |

### Debug Checklist

```
1. ✅ Check health endpoint: GET /api/health
2. ✅ Review service_status dictionary
3. ✅ Check application logs: logs/error.log
4. ✅ Verify API keys and credentials
5. ✅ Test individual service endpoints
6. ✅ Check network/internet connectivity
7. ✅ Restart the application
8. ✅ Review error messages in logs
```

---

## Best Practices

### DO ✅
- ✅ Always wrap service initialization in try-catch
- ✅ Check service availability before using it
- ✅ Log errors with context information
- ✅ Return appropriate HTTP status codes
- ✅ Include service status in error responses
- ✅ Test endpoints when services are degraded
- ✅ Use retry logic for transient failures

### DON'T ❌
- ❌ Let one service crash the entire application
- ❌ Return generic "500 Error" messages
- ❌ Forget to update service_status on initialization
- ❌ Use services without checking availability
- ❌ Ignore or hide errors - log them!
- ❌ Block requests when a service is down (unless critical)
- ❌ Assume external APIs are always available

---

## Architecture Diagram

```
┌─────────────────────────────────────────────────────┐
│               Batuma Application                    │
├─────────────────────────────────────────────────────┤
│                                                     │
│  ┌──────────────────────────────────────────────┐   │
│  │         Global Error Handlers                │   │
│  │  - 404 Not Found                             │   │
│  │  - 500 Internal Server Error                 │   │
│  │  - 503 Service Unavailable                   │   │
│  └──────────────────────────────────────────────┘   │
│                                                     │
│  ┌──────────────┐ ┌──────────────┐                  │
│  │ User Manager │ │Alert Engine  │ (Independent)   │
│  │              │ │              │                  │
│  │ Status: ON   │ │ Status: OFF   │                 │
│  └──────────────┘ └──────────────┘                  │
│                                                     │
│  ┌──────────────┐ ┌──────────────┐                  │
│  │ Geocoding    │ │Google Routes │ (Independent)   │
│  │              │ │              │                  │
│  │ Status: ON   │ │ Status: ON    │                 │
│  └──────────────┘ └──────────────┘                  │
│                                                     │
│  ┌──────────────┐ ┌──────────────┐                  │
│  │ Transit API  │ │Firestore DB  │ (Dependent)     │
│  │              │ │              │                  │
│  │ Status: ON   │ │ Status: ON    │                 │
│  └──────────────┘ └──────────────┘                  │
│                                                     │
│  ALL SERVICES INDEPENDENT - FAILURES ISOLATED      │
└─────────────────────────────────────────────────────┘
```

---

## Summary

The Batuma application implements **resilient, fault-tolerant** architecture where:

✅ **Services are independently initialized** - one failure doesn't cascade
✅ **Every endpoint checks service availability** - before using any service
✅ **HTTP status codes indicate service state** - 503 when service unavailable
✅ **Errors are logged and tracked** - for monitoring and debugging
✅ **Clients receive detailed error responses** - with service status info
✅ **Other services continue working** - even when one is down
✅ **Graceful degradation** - users see helpful messages, not crashes

This approach ensures **maximum uptime** and **better user experience** even during service disruptions.

---

**Last Updated:** January 17, 2026  
**Version:** 1.0  
**Status:** ✅ Production Ready
