@echo off
title AutoCare AI - Mobile Phone Connect
echo ======================================================================
echo           AutoCare AI - Mobile Phone Connection Helper
echo ======================================================================
echo.

cd /d "%~dp0"

:: Detect Local LAN IP
for /f "usebackq tokens=*" %%i in (`python -c "import socket; s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM); s.connect(('8.8.8.8', 80)); print(s.getsockname()[0]); s.close()" 2^>nul`) do set LOCAL_IP=%%i
if "%LOCAL_IP%"=="" set LOCAL_IP=127.0.0.1

:: Check if server is running, if not start it on 0.0.0.0
netstat -ano | findstr :8000 | findstr LISTENING >nul 2>&1
if %errorlevel% neq 0 (
    echo [INFO] Starting AutoCare AI server on port 8000 across all interfaces (0.0.0.0)...
    start /b python -m uvicorn autocare.api:app --host 0.0.0.0 --port 8000 --app-dir "%~dp0backend"
    timeout /t 3 /nobreak >nul
)

echo.
echo ======================================================================
echo                 HOW TO OPEN ON YOUR MOBILE PHONE
echo ======================================================================
echo  1. Make sure your mobile phone is connected to the SAME Wi-Fi network.
echo  2. Open Chrome, Safari, or Samsung Internet on your phone.
echo  3. Type the following URL in your mobile browser's address bar:
echo.
echo       http://%LOCAL_IP%:8000/app/#/dashboard
echo.
echo ======================================================================
echo  Tip: You can also bookmark it or tap "Add to Home Screen" on your
echo       phone to use AutoCare AI just like a native mobile app!
echo ======================================================================
echo.
pause
