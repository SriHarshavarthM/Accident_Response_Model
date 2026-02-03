@echo off
title Stop All Services
color 0C

echo ========================================
echo    Stopping All Services
echo ========================================
echo.

:: Kill Python (backend)
echo Stopping Backend...
taskkill /f /im python.exe 2>nul
if errorlevel 1 (
    echo Backend was not running
) else (
    echo [OK] Backend stopped
)

:: Kill Node (frontend)
echo Stopping Frontend...
taskkill /f /im node.exe 2>nul
if errorlevel 1 (
    echo Frontend was not running
) else (
    echo [OK] Frontend stopped
)

echo.
echo ========================================
echo    All services stopped
echo ========================================
pause
