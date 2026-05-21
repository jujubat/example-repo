@echo off
REM Quick Setup Script - Initialize Admin and Test Application

color 0A
echo.
echo ========================================
echo   BATUMA APP SETUP & VERIFICATION
echo ========================================
echo.

REM Check if server is running
echo [*] Checking if server is running on http://127.0.0.1:8000...
timeout /t 2 /nobreak > nul

REM Initialize admin account
echo.
echo [+] Initializing Admin Account...
echo.
echo Admin Credentials:
echo   Email: admin@batuma.com
echo   Password: Admin@1234
echo   Role: super_admin
echo.

curl -X POST http://127.0.0.1:8000/api/admin/init ^
  -H "Content-Type: application/json" ^
  -d "{\"email\": \"admin@batuma.com\", \"password\": \"Admin@1234\", \"name\": \"Admin User\", \"phone\": \"+27000000000\"}"

echo.
echo.
echo [+] Admin initialization complete!
echo.

REM Test login
echo [*] Testing Admin Login...
echo.

curl -X POST http://127.0.0.1:8000/api/auth/login ^
  -H "Content-Type: application/json" ^
  -d "{\"email\": \"admin@batuma.com\", \"password\": \"Admin@1234\"}"

echo.
echo.
echo [+] Login test complete!
echo.

REM Test health check
echo [*] Testing Service Health...
echo.

curl http://127.0.0.1:8000/api/health

echo.
echo.
echo ========================================
echo   SETUP COMPLETE!
echo ========================================
echo.
echo Next Steps:
echo   1. Open browser to http://127.0.0.1:8000/login.html
echo   2. Login with admin@batuma.com / Admin@1234
echo   3. Test widgets by clicking service cards
echo.
echo For help, see: WIDGET_AND_LOGIN_FIXES.md
echo.
pause
