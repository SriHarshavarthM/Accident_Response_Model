@echo off
title Accident Incident Responder - Setup & Run
color 0A

echo ========================================================
echo    Accident Incident Responder System
echo    Setup and Run Script
echo ========================================================
echo.

:: Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH
    echo Please install Python 3.9+ from https://python.org
    pause
    exit /b 1
)

:: Check if Node.js is installed
node --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Node.js is not installed or not in PATH
    echo Please install Node.js 18+ from https://nodejs.org
    pause
    exit /b 1
)

echo [OK] Python found
echo [OK] Node.js found
echo.

:: Setup Backend
echo ========================================================
echo [1/4] Setting up Backend...
echo ========================================================
cd backend

:: Create virtual environment if not exists
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

:: Activate venv and install dependencies
call venv\Scripts\activate.bat
echo Installing Python dependencies...
pip install -r requirements.txt --quiet

:: Seed database
echo Seeding database with demo data...
python seed_data.py

cd ..
echo [OK] Backend setup complete
echo.

:: Setup Frontend
echo ========================================================
echo [2/4] Setting up Frontend...
echo ========================================================
cd frontend

:: Install npm dependencies
if not exist "node_modules" (
    echo Installing npm dependencies...
    call npm install
) else (
    echo [OK] Dependencies already installed
)

cd ..
echo [OK] Frontend setup complete
echo.

:: Start Services
echo ========================================================
echo [3/4] Starting Backend Server...
echo ========================================================
start "Backend API" cmd /k "cd backend && call venv\Scripts\activate.bat && python main.py"

:: Wait for backend to start
echo Waiting for backend to initialize...
timeout /t 5 /nobreak >nul

echo ========================================================
echo [4/4] Starting Frontend Server...
echo ========================================================
start "Frontend Dashboard" cmd /k "cd frontend && npm run dev"

:: Wait for frontend to start
timeout /t 3 /nobreak >nul

echo.
echo ========================================================
echo    ALL SERVICES STARTED SUCCESSFULLY!
echo ========================================================
echo.
echo    Frontend Dashboard: http://localhost:3000
echo    Backend API:        http://localhost:8000
echo    API Documentation:  http://localhost:8000/docs
echo.
echo    Press any key to open the dashboard in browser...
pause >nul

:: Open browser
start http://localhost:3000

echo.
echo To stop the services, close the terminal windows.
echo.
