@echo off
setlocal enabledelayedexpansion
cd /d "%~dp0backend"

echo ========================================================================
echo   AI AUTO PAKISTAN - ONE-CLICK AUTOMATIC DATASET COLLECTOR (NO PORT)
echo ========================================================================
echo.

if not exist ".env" (
    if exist ".env.example" (
        copy /Y ".env.example" ".env" >nul
        echo Created backend\.env from .env.example
    )
)

set "YT_KEY="
if exist ".env" (
    for /f "usebackq tokens=1,* delims==" %%A in (".env") do (
        if "%%A"=="YOUTUBE_API_KEY" set "YT_KEY=%%B"
    )
)

if "%YT_KEY%"=="" (
    echo [NOTE] YOUTUBE_API_KEY is not set in backend\.env yet.
    set /p "INPUT_KEY=Paste your YouTube Data API v3 Key (or press Enter to skip YouTube): "
    if not "!INPUT_KEY!"=="" (
        set "YOUTUBE_API_KEY=!INPUT_KEY!"
        echo YOUTUBE_API_KEY=!INPUT_KEY!>> ".env"
        echo Saved YOUTUBE_API_KEY into backend\.env
    )
)

echo.
echo Running autonomous collector, cleaner, damage-screenshot extractor, and local bundler...
python -m data_engine.auto_collect_bundle --all-queries --include-cc-search --local-videos-dir "%~dp0Consented_Mechanic_Videos"

echo.
echo Done! Opening offline local viewer...
start "" "%~dp0AI_Auto_Pakistan_Dataset\dataset_viewer.html"
pause
