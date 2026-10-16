@echo off
REM AutoCare AI - start the API and the app.  Double-click this file.
REM Put your Groq key below ONCE. Never share or upload this file with the key in it.

cd /d "%~dp0"
call .venv\Scripts\activate

set AUTOCARE_DATABASE_URL=sqlite:///autocare_real.db
set AUTOCARE_ML_BACKEND=models
set AUTOCARE_GENERATION_MODE=llm
set AUTOCARE_LLM_BASE_URL=https://api.groq.com/openai/v1
set AUTOCARE_LLM_MODEL=openai/gpt-oss-120b
set AUTOCARE_LLM_API_KEY=PASTE_YOUR_GROQ_KEY_HERE
REM Story 3: read fault codes from scanner photos with Groq's vision model.
set AUTOCARE_CODE_READER=vision
set AUTOCARE_VISION_MODEL=qwen/qwen3.8-27b

echo.
echo Starting AutoCare AI... the models take about a minute to load.
echo When you see "Application startup complete", open:  http://localhost:8000/app/
echo Keep this window open. Press Ctrl+C to stop.
echo.
python -m uvicorn autocare.api:app --reload
pause
