@echo off
title Quick Start - Accident Incident Responder
color 0B

echo ========================================
echo    Quick Start (assumes setup done)
echo ========================================
echo.

:: Start Backend
echo Starting Backend API...
start "Backend API" cmd /k "cd backend && call venv\Scripts\activate.bat && python main.py"

timeout /t 3 /nobreak >nul

:: Start Frontend
echo Starting Frontend Dashboard...
start "Frontend Dashboard" cmd /k "cd frontend && npm run dev"

timeout /t 3 /nobreak >nul

echo.
echo ========================================
echo    Services Started!
echo ========================================
echo    Frontend: http://localhost:3000
echo    Backend:  http://localhost:8000
echo ========================================
echo.

:: Open browser
start http://localhost:3000
