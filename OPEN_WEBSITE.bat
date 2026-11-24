@echo off
title AutoCare AI Web Portal & Mobile Launcher
echo ======================================================================
echo           Starting AutoCare AI Web Portal (Desktop & Mobile)
echo ======================================================================
echo.

:: Detect Local Network IP for Phone & Friends
for /f "usebackq tokens=*" %%i in (`python -c "import socket; s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM); s.connect(('8.8.8.8', 80)); print(s.getsockname()[0]); s.close()" 2^>nul`) do set LOCAL_IP=%%i
if "%LOCAL_IP%"=="" set LOCAL_IP=127.0.0.1

netstat -ano | findstr :8000 | findstr LISTENING >nul 2>&1
if %errorlevel% neq 0 (
    echo [INFO] AutoCare server is starting on port 8000 (0.0.0.0)...
    start /b python -m uvicorn autocare.api:app --host 0.0.0.0 --port 8000 --app-dir "%~dp0backend"
    timeout /t 3 /nobreak >nul
) else (
    echo [OK] AutoCare server is already active on port 8000.
)

echo [INFO] Opening Web Portal in your default browser...
start http://localhost:8000/app/#/dashboard

echo ======================================================================
echo [DESKTOP] Open on this computer:
echo           http://localhost:8000/app/#/dashboard
echo.
echo [MOBILE / PHONE] Open on your smartphone (connect to same Wi-Fi):
echo           http://%LOCAL_IP%:8000/app/#/dashboard
echo ======================================================================
echo.
pause
