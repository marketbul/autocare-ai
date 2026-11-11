@echo off
title AutoCare AI Web Portal Launcher
echo ======================================================================
echo           Starting AutoCare AI Web Portal (Unified App)
echo ======================================================================
echo.

netstat -ano | findstr :8000 | findstr LISTENING >nul 2>&1
if %errorlevel% neq 0 (
    echo [INFO] AutoCare server is starting on port 8000...
    start /b python -m uvicorn autocare.api:app --host 127.0.0.1 --port 8000 --app-dir "C:\Users\ABDUL\.gemini\antigravity\scratch\autocare-us2\backend"
    timeout /t 3 /nobreak >nul
) else (
    echo [OK] AutoCare server is already active on port 8000.
)

echo [INFO] Opening Web Portal in your default browser...
start http://localhost:8000/app/#/dashboard

echo [SUCCESS] AutoCare AI is running at:
echo http://localhost:8000/app/#/dashboard
echo.
