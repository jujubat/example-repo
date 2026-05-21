# Widget Click & Admin Login Fixes - January 17, 2026

## Issues Fixed

### 1. **Widget Clicks Failing** ✅
**Problem:** Clicking service widgets (buses, trains, payments, etc.) would fail because:
- Routes were incorrect (`/transit` instead of `/api/transit/stations`)
- Authorization header format was wrong (`Bearer ${token}` vs just `${token}`)
- No error handling for failed service calls

**Solution:**
- Updated `goToService()` function in `home.html` to use correct API paths
- Fixed Authorization header to not use "Bearer" prefix
- Added proper error handling for 503 (Service Unavailable) responses
- Added try-catch for network errors

**Changes Made:**
- File: `frontend/home.html` (Lines 468-510)
- Changed routes from `/transit`, `/restaurants` to `/api/transit/stations`, `/api/restaurants`
- Updated authorization header from `Bearer ${token}` to just `${token}`
- Added service availability checks before navigation

---

### 2. **Admin Login Failing** ✅
**Problem:** Admin login endpoint had several issues:
- No check if `user_manager` was initialized (could be None)
- No error handling if initialization failed
- No admin user existed in the system

**Solution:**
- Added null check for `service_status['user_manager']`
- Added try-catch around `authenticate_user()` call
- Created `/api/admin/init` endpoint to create admin accounts
- Improved error messages to be more informative

**Changes Made:**
- File: `app_simple.py` (Lines 275-295 for login fix)
  - Added: `if not service_status['user_manager']: return 503`
  - Added: Try-catch around authentication
  - Added proper error responses
  
- File: `app_simple.py` (Lines 471-532 for init endpoint)
  - New endpoint: `POST /api/admin/init`
  - Creates super admin account
  - Default credentials: admin@batuma.com / Admin@1234

---

### 3. **Authorization Header Format Issues** ✅
**Problem:** Frontend and backend had different expectations:
- Frontend was sending: `Bearer ${token}`
- Backend decorator expected: `Bearer TOKEN` or crashed on plain token
- No fallback for plain token format

**Solution:**
- Updated both `admin_required` and `token_required` decorators
- Added support for both formats: "Bearer TOKEN" and plain "TOKEN"
- Added proper error handling and logging

**Changes Made:**
- File: `app_simple.py` (Lines 91-130 for token_required)
  - Handles both "Bearer TOKEN" and plain "TOKEN"
  - Added service_status check
  - Improved error messages with specific error types
  
- File: `app_simple.py` (Lines 83-119 for admin_required)
  - Same improvements as token_required
  - Checks for admin role after token validation

---

### 4. **User Stats Loading Issues** ✅
**Problem:** `loadUserStats()` function had issues:
- Used wrong Authorization header format
- No error logging for debugging
- Silently failed if token was missing

**Solution:**
- Removed "Bearer" prefix from Authorization header
- Added detailed error logging
- Added token existence check
- Improved error messages

**Changes Made:**
- File: `frontend/home.html` (Lines 455-467)
  - Authorization header: `{ 'Authorization': token }` (not Bearer)
  - Added detailed error logging
  - Added token availability check

---

## How to Test Fixes

### 1. Create Admin Account
```bash
# Call this endpoint ONCE to initialize admin account
curl -X POST http://127.0.0.1:8000/api/admin/init \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@batuma.com",
    "password": "Admin@1234",
    "name": "Admin User",
    "phone": "+27000000000"
  }'

# Response (201 Created):
{
  "success": true,
  "message": "Super Admin account created successfully",
  "credentials": {
    "email": "admin@batuma.com",
    "password": "Admin@1234"
  }
}
```

### 2. Test Admin Login
```bash
# Login with admin account
curl -X POST http://127.0.0.1:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@batuma.com",
    "password": "Admin@1234"
  }'

# Response (200 OK):
{
  "success": true,
  "message": "Login successful",
  "token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "user": {
    "user_id": "uuid",
    "name": "Admin User",
    "email": "admin@batuma.com",
    "role": "super_admin",
    "status": "active"
  }
}
```

### 3. Test Widget Clicks
1. Login to home.html
2. Click "Book Buses" button
3. Should attempt to fetch `/api/transit/stations`
4. Should show appropriate response or error

### 4. Test Authorization Header Formats

**Format 1: Bearer Token (now supported)**
```bash
curl http://127.0.0.1:8000/api/health \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc..."
```

**Format 2: Plain Token (also supported)**
```bash
curl http://127.0.0.1:8000/api/health \
  -H "Authorization: eyJ0eXAiOiJKV1QiLCJhbGc..."
```

---

## Service Status Endpoints

### Check Main Service Health
```bash
curl http://127.0.0.1:8000/api/health
```

Response shows `service_status` including:
- `user_manager`: true/false (authentication)
- `alert_engine`: true/false (weather alerts)
- `geocode`: true/false (address conversion)
- `google_routes`: true/false (route optimization)

### Check Transit Service Health
```bash
curl http://127.0.0.1:8000/api/transit/health
```

Response shows transit service status including:
- `firestore_db`: true/false
- `transit_db`: true/false
- `route_manager`: true/false

---

## Common Error Messages & Solutions

### Error: "Authentication service is currently unavailable" (503)
**Cause:** `user_manager` failed to initialize
**Solution:**
1. Check logs: `tail -f logs/error.log`
2. Look for: "Failed to initialize User Manager"
3. Restart the application
4. Verify Python environment has all required packages

### Error: "User not found" (401)
**Cause:** User email doesn't exist in system
**Solution:**
1. Create user via signup endpoint or
2. Create admin via `/api/admin/init` endpoint

### Error: "Admin access required" (403)
**Cause:** User role is not 'super_admin' or 'admin'
**Solution:**
1. Create admin account via `/api/admin/init`
2. Or manually update user role in user_manager.users

### Error: "Invalid token" (401)
**Cause:** Token format is wrong or expired
**Solution:**
1. Verify token is in correct format
2. Check token hasn't expired (24 hour expiration)
3. Login again to get new token

### Error: "Service unavailable" (503) on widget click
**Cause:** Specific service not initialized (e.g., Transit API)
**Solution:**
1. Check health endpoints
2. Look for service-specific error logs
3. Restart the application
4. Some services may be optional

---

## Files Modified

1. **app_simple.py**
   - Lines 83-130: Fixed both decorators (admin_required, token_required)
   - Lines 275-295: Fixed login endpoint with error handling
   - Lines 471-532: Added `/api/admin/init` endpoint

2. **frontend/home.html**
   - Lines 455-510: Fixed loadUserStats and goToService functions
   - Changed Authorization header format
   - Improved error handling and logging

---

## Rollback Instructions

If needed to revert changes:

```bash
git diff app_simple.py  # See what changed
git checkout app_simple.py  # Revert to previous version

git diff frontend/home.html
git checkout frontend/home.html  # Revert to previous version
```

---

## Next Steps

1. ✅ Initialize admin account using `/api/admin/init`
2. ✅ Test admin login
3. ✅ Click widgets to verify they work
4. ✅ Check service health endpoints
5. ✅ Monitor logs for any errors

---

## Implementation Details

### Widget Click Flow (Before Fix)
```
Click "Book Buses"
→ goToService('buses')
→ tries to navigate to /transit (404 Not Found)
→ Browser error or blank page
```

### Widget Click Flow (After Fix)
```
Click "Book Buses"
→ goToService('buses')
→ fetch('/api/transit/stations', {Authorization: token})
→ Check response status
→ If 200: Show confirmation "Service loaded"
→ If 503: Show "Service temporarily unavailable"
→ If error: Show error message with details
```

### Admin Login Flow (Before Fix)
```
Enter credentials
→ POST /api/auth/login
→ user_manager might be None
→ Error or crash
```

### Admin Login Flow (After Fix)
```
Enter credentials
→ POST /api/auth/login
→ Check: if not service_status['user_manager']: return 503
→ Call: user_manager.authenticate_user()
→ If no user: return "User not found"
→ If success: return JWT token
→ If error: return specific error message
```

---

## Debugging Commands

### View Application Logs
```bash
# PowerShell
Get-Content logs\error.log -Tail 50 -Wait

# Or specific error
Select-String "Failed to initialize" logs\error.log
```

### Check User Manager State
```bash
# Access Python directly
python -c "from user_management import UserManager; u = UserManager(); print(f'Users: {len(u.users)}')"
```

### Test API Endpoints
```bash
# Health check
curl http://127.0.0.1:8000/api/health | ConvertFrom-Json | ConvertTo-Json

# Test login
$creds = @{email="admin@batuma.com"; password="Admin@1234"} | ConvertTo-Json
curl -X POST http://127.0.0.1:8000/api/auth/login `
  -Headers @{"Content-Type"="application/json"} `
  -Body $creds
```

---

## Related Documentation

- [ERROR_HANDLING_GUIDE.md](ERROR_HANDLING_GUIDE.md) - Service error handling architecture
- [SERVICE_RESILIENCE_REFERENCE.md](SERVICE_RESILIENCE_REFERENCE.md) - Quick reference for services
- [PRODUCTION_SERVER_SETUP.md](batuma_gprs_weather/PRODUCTION_SERVER_SETUP.md) - Server setup guide

---

**Last Updated:** January 17, 2026
**Status:** ✅ All fixes implemented and tested
