@echo off
cd /d "%~dp0backend"

echo ========================================================================
echo   AI AUTO PAKISTAN - LOCAL FACEBOOK Q&A & CONSENTED MEDIA IMPORTER
echo ========================================================================
echo.
echo Ingesting curated Q&A files from Facebook_Community_QA\ and rebuilding bundle...
python -m data_engine.auto_collect_bundle --skip-youtube --local-videos-dir "%~dp0Consented_Mechanic_Videos" --local-facebook-dir "%~dp0Facebook_Community_QA"

echo.
echo Done! Opening offline local viewer...
start "" "%~dp0AI_Auto_Pakistan_Dataset\dataset_viewer.html"
pause
