@echo off
title AutoCare AI - New Laptop 1-Click Setup & Launcher
echo ======================================================================
echo           AutoCare AI - Automated 1-Click Setup for Team
echo ======================================================================
echo.

cd /d "%~dp0"

echo [1/3] Checking Python installation...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not in PATH!
    echo Please install Python 3.10+ from python.org and check "Add Python to PATH".
    pause
    exit /b 1
)
echo [OK] Python is available.
echo.

echo [2/3] Installing Python backend dependencies...
pip install -r backend\requirements.txt
if %errorlevel% neq 0 (
    echo [WARNING] Some dependencies failed, proceeding with standard runner...
)
echo.

echo [3/3] Launching AutoCare AI Web Portal...
start OPEN_WEBSITE.bat

echo ======================================================================
echo [SUCCESS] AutoCare AI is ready and running!
echo Portal URL: http://localhost:8000/app/#/dashboard
echo ======================================================================
echo.
pause
