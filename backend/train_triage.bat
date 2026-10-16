@echo off
REM AutoCare AI - train the Story 4 urgency classifier and print its results.
REM Double-click this file. It needs no API key. Takes a few minutes the first time.

cd /d "%~dp0"
call .venv\Scripts\activate

set AUTOCARE_DATABASE_URL=sqlite:///autocare_real.db
set AUTOCARE_ML_BACKEND=models

echo.
echo Training the urgency classifier with BGE-M3... please wait.
echo.
python -m ingest.train_triage --baseline > train_triage_output.txt 2>&1
type train_triage_output.txt
echo.
echo Done. The results above are also saved in train_triage_output.txt - send that file to Claude.
echo The model is saved in models\triage.pkl and start.bat will use it.
echo.
pause
