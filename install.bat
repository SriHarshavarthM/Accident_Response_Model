@echo off
title Install Only - Accident Incident Responder
color 0E

echo ========================================================
echo    Accident Incident Responder - Install Dependencies
echo ========================================================
echo.

:: Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found. Please install Python 3.9+
    pause
    exit /b 1
)

:: Check Node
node --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Node.js not found. Please install Node.js 18+
    pause
    exit /b 1
)

echo [1/3] Setting up Backend...
cd backend
if not exist "venv" (
    python -m venv venv
)
call venv\Scripts\activate.bat
pip install -r requirements.txt
python seed_data.py
cd ..
echo [OK] Backend ready

echo.
echo [2/3] Setting up Frontend...
cd frontend
call npm install
cd ..
echo [OK] Frontend ready

echo.
echo [3/3] Setting up ML Engine...
cd ml
pip install -r requirements.txt 2>nul || echo No ML requirements yet
cd ..
echo [OK] ML Engine ready

echo.
echo ========================================================
echo    Installation Complete!
echo ========================================================
echo.
echo    Run 'start.bat' to launch the application
echo    Or run 'run.bat' for full setup + launch
echo.
pause
