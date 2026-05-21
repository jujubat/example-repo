@echo off
REM =========================================
REM Batuma Production WSGI Server Launcher
REM Starts Gunicorn on port 8000
REM =========================================

setlocal enabledelayedexpansion

echo.
echo =========================================
echo Batuma Multi-Service Platform
echo Production WSGI Server (Gunicorn)
echo =========================================
echo.

REM Get the directory of this batch file
set "SCRIPT_DIR=%~dp0"
cd /d "%SCRIPT_DIR%"

REM Check if Python virtual environment exists
if not exist ".venv\Scripts\python.exe" (
    echo [ERROR] Virtual environment not found at .venv
    echo [INFO] Please run setup first
    pause
    exit /b 1
)

REM Create logs directory
if not exist "logs" mkdir logs

REM Set environment variables
set ENVIRONMENT=production
set FLASK_ENV=production
set FLASK_DEBUG=False
set GUNICORN_BIND=0.0.0.0:8000
set GUNICORN_WORKERS=4
set GUNICORN_ACCESS_LOG=logs/access.log
set GUNICORN_ERROR_LOG=logs/error.log

echo [INFO] Environment: %ENVIRONMENT%
echo [INFO] Binding to: %GUNICORN_BIND%
echo [INFO] Workers: %GUNICORN_WORKERS%
echo [INFO] Access Log: %GUNICORN_ACCESS_LOG%
echo [INFO] Error Log: %GUNICORN_ERROR_LOG%
echo.
echo [STARTUP] Starting Gunicorn server...
echo.

REM Start Gunicorn
.venv\Scripts\gunicorn.exe -c gunicorn_config.py wsgi:application

if errorlevel 1 (
    echo [ERROR] Gunicorn failed to start
    pause
    exit /b 1
)

pause
    exit /b 1
)

pause
