@echo off
REM Batuma GPRS Weather - Production Server (Waitress)
REM Windows-friendly WSGI server for production deployment

echo.
echo =====================================================
echo   Batuma GPRS Weather - Production Server
echo   Using: Waitress WSGI Server
echo   Platform: Windows
echo =====================================================
echo.

REM Get to the correct directory
cd /d "%~dp0"

REM Check if virtual environment exists
if not exist ".venv" (
    echo [ERROR] Virtual environment not found (.venv)
    echo [INFO] Please run: python -m venv .venv
    pause
    exit /b 1
)

REM Activate virtual environment
call .venv\Scripts\activate.bat
if errorlevel 1 (
    echo [ERROR] Failed to activate virtual environment
    pause
    exit /b 1
)

REM Check if Waitress is installed
python -c "import waitress" >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Waitress not installed
    echo [INFO] Installing: pip install waitress
    pip install waitress
    if errorlevel 1 (
        echo [ERROR] Failed to install Waitress
        pause
        exit /b 1
    )
)

REM Create logs directory
if not exist "logs" (
    mkdir logs
    echo [INFO] Created logs directory
)

REM Set environment variables
set ENVIRONMENT=production
set FLASK_ENV=production
set FLASK_DEBUG=False
set WAITRESS_HOST=127.0.0.1
set WAITRESS_PORT=8000
set WAITRESS_THREADS=4

echo [INFO] Environment:
echo   - ENVIRONMENT: %ENVIRONMENT%
echo   - FLASK_ENV: %FLASK_ENV%
echo   - FLASK_DEBUG: %FLASK_DEBUG%
echo.

echo [INFO] Waitress Configuration:
echo   - Host: %WAITRESS_HOST%
echo   - Port: %WAITRESS_PORT%
echo   - Threads: %WAITRESS_THREADS%
echo.

REM Start server using Python directly
echo [STARTUP] Starting Waitress server...
echo [INFO] Server starting on http://%WAITRESS_HOST%:%WAITRESS_PORT%
echo [INFO] Access frontend at http://127.0.0.1:8000/frontend/home.html
echo [INFO] API health check: http://127.0.0.1:8000/api/health
echo [INFO] Press Ctrl+C to stop
echo.

python -c "
import sys
import os
sys.path.insert(0, os.path.join(os.getcwd(), 'batuma_gprs_weather'))
os.chdir(os.path.join(os.getcwd(), 'batuma_gprs_weather'))
from app_simple import app
from waitress import serve
serve(app, host='127.0.0.1', port=8000, threads=4)
"

if errorlevel 1 (
    echo.
    echo [ERROR] Server exited with error code: %errorlevel%
    pause
)
