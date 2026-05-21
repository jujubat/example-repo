# Troubleshooting Guide - January 17, 2026 Updates

## Weather API Issues

### Problem: "Could not find location" error
**Causes:**
1. Misspelled city/place name
2. Google Maps API key not configured
3. Network connectivity issue

**Solutions:**
- ✅ Check spelling carefully
- ✅ Verify `GOOGLE_MAPS_API_KEY` environment variable is set
- ✅ Test API key with direct Google Maps call
- ✅ Check internet connection

### Problem: Weather returns empty data
**Causes:**
1. Visual Crossing API key invalid
2. Coordinates out of service area
3. API rate limit exceeded

**Solutions:**
- ✅ Verify `VC_API_KEY` is correct
- ✅ Try different location
- ✅ Wait 1 minute before retrying (rate limit)
- ✅ Check API fallback (OpenWeather) has valid key

### Problem: Slow weather response
**Causes:**
1. Cache miss (new location)
2. Network latency
3. API timeout

**Solutions:**
- ✅ Subsequent calls for same location will be faster (cached)
- ✅ Check network connectivity
- ✅ Verify API timeout setting (default 5 seconds)

---

## Travel Time Issues

### Problem: "Could not calculate route" error
**Causes:**
1. Start or end location not found
2. No road route between locations
3. Google Maps API not configured

**Solutions:**
- ✅ Use exact addresses (street + city)
- ✅ Verify locations are accessible by road
- ✅ Check `GOOGLE_MAPS_API_KEY` is set
- ✅ Test with well-known locations first (e.g., "Big Ben, London")

### Problem: Distance/time seems incorrect
**Causes:**
1. Geocoding returned wrong coordinates
2. Google Maps providing walking route instead of driving
3. Traffic conditions not factored in

**Solutions:**
- ✅ Use full addresses instead of just place names
- ✅ Verify coordinates using `/api/weather/by-place` first
- ✅ Current implementation uses Google Maps defaults
- ✅ Note: Real-time traffic not included in basic routes

### Problem: No routes returned
**Causes:**
1. Destination not reachable by road
2. Geocoding failed silently
3. API error not visible

**Solutions:**
- ✅ Try major cities/streets first to verify setup
- ✅ Check browser console for JavaScript errors
- ✅ Verify both `GOOGLE_MAPS_API_KEY` is working
- ✅ Test endpoint directly with curl

---

## Bus/Train Route Issues

### Problem: "Invalid transit_type" error
**Causes:**
1. Typo in transit_type (not "bus" or "train")
2. Wrong parameter name used

**Solutions:**
- ✅ Use exactly: `"transit_type": "bus"` or `"transit_type": "train"`
- ✅ Check request body format matches documentation
- ✅ Verify JSON syntax is correct

### Problem: No routes found in area
**Causes:**
1. No stations in database for that area
2. Radius too small
3. Wrong transit_type

**Solutions:**
- ✅ Check if stations are loaded in database
- ✅ Increase `radius_km` (try 5.0 instead of 1.0)
- ✅ Try both "bus" and "train"
- ✅ Use `/api/transit/stations/all` to see available stations

### Problem: Routes missing category information
**Causes:**
1. Routes created before update don't have category field
2. Category value is NULL in database

**Solutions:**
- ✅ New routes automatically get default category "local"
- ✅ Update existing routes: use category filter as "local"
- ✅ Or recreate routes with category parameter

### Problem: Location search not finding routes
**Causes:**
1. Location name doesn't match station names
2. Case sensitivity issue
3. Partial name not matching

**Solutions:**
- ✅ Use full station names (e.g., "Central Bus Station" not just "Central")
- ✅ Search is case-insensitive, so capitalization doesn't matter
- ✅ Use exact names or major landmarks
- ✅ Try `/api/transit/stations/search?q=location_name` first

---

## Frontend Issues

### Problem: Routes button doesn't show travel time
**Causes:**
1. API endpoints not responding
2. Frontend not updated
3. Browser cache issues

**Solutions:**
- ✅ Clear browser cache (Ctrl+Shift+Delete)
- ✅ Verify backend server is running
- ✅ Check browser console for errors (F12)
- ✅ Reload page (Ctrl+F5)

### Problem: Weather section still visible
**Causes:**
1. Cached HTML version
2. Frontend files not updated

**Solutions:**
- ✅ Clear browser cache
- ✅ Hard refresh (Ctrl+F5)
- ✅ Clear all browser data for the domain
- ✅ Restart browser

### Problem: API_BASE_URL undefined error
**Causes:**
1. app.js not loaded correctly
2. server configuration issue

**Solutions:**
- ✅ Check browser console (F12)
- ✅ Verify app.js is loading
- ✅ Check for JavaScript errors
- ✅ Restart backend server

---

## General Troubleshooting

### Debug Mode
**Enable logging for more details:**
```python
# In app_simple.py
logging.basicConfig(level=logging.DEBUG)
```

### Test API Endpoints
```bash
# Test weather endpoint
curl -X POST http://localhost:8000/api/weather/by-place \
  -H "Content-Type: application/json" \
  -d '{"city": "London"}'

# Test travel time
curl -X POST http://localhost:8000/api/routes/travel-time \
  -H "Content-Type: application/json" \
  -d '{
    "start_place": "London",
    "end_place": "Manchester"
  }'

# Test transit categories
curl http://localhost:8000/api/transit/categories
```

### Check Environment Variables
```bash
# Linux/Mac
echo $GOOGLE_MAPS_API_KEY
echo $VC_API_KEY

# Windows PowerShell
$env:GOOGLE_MAPS_API_KEY
$env:VC_API_KEY
```

### Restart Services
```bash
# Restart backend
python app_simple.py

# Or with gunicorn
gunicorn -c gunicorn_config.py app_simple:app
```

---

## Known Limitations

1. **Weather Caching**: Results cached for 10 minutes per location
2. **API Rate Limits**: Google Maps free tier has limits (~25,000 requests/day)
3. **Geocoding Accuracy**: May return unexpected results for ambiguous addresses
4. **Travel Time**: Uses Google Maps defaults (driving, no real-time traffic)
5. **Transit Data**: Only shows routes that are in database

---

## Performance Optimization Tips

### 1. Reduce API Calls
- Cache results where possible
- Reuse coordinates for weather

### 2. Optimize Queries
- Limit station search radius
- Use specific location names

### 3. Database Indexes
- Ensure transit_stations has index on `station_type`
- Ensure transit_routes has index on `transit_type`, `category`

### 4. Frontend Optimization
- Lazy load route data
- Debounce API requests
- Cache route results client-side

---

## Support Resources

| Issue Type | Resource |
|-----------|----------|
| Google Maps API | https://developers.google.com/maps/documentation |
| Visual Crossing | https://www.visualcrossing.com/resources/documentation |
| OpenWeather | https://openweathermap.org/api |
| Flask Documentation | https://flask.palletsprojects.com/ |

---

## Reporting Issues

When reporting a bug, include:
1. ✅ Error message (exact text)
2. ✅ Request body (if API call)
3. ✅ Response code (HTTP status)
4. ✅ Server logs (if available)
5. ✅ Environment variables (without sensitive data)
6. ✅ Steps to reproduce

---

**Last Updated:** January 17, 2026  
**Status:** Troubleshooting guide v1.0
