@echo off
REM Start PS-03 API Server
echo Starting PS-03 API Server...
echo.

REM Activate virtual environment if it exists
if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate.bat
)

REM Start API
python api\main.py

pause
