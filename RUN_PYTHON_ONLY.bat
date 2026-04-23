@echo off
echo ========================================
echo   Python-Only Trading System
echo     (No C Compilation Required)
echo ========================================
echo.

echo [1/2] Starting Python FastAPI Server...
cd server
start "Python Server" cmd /k "python main.py"
timeout /t 3 /nobreak >nul

echo [2/2] Opening Trading Dashboard...
cd ..
start "" "http://localhost:8000"
timeout /t 2 /nobreak >nul
start "" "frontend\index.html"

echo.
echo ========================================
echo    Python Trading System Started!
echo ========================================
echo.
echo NOTE: This runs without C Bot.
echo Market data will be simulated in Python.
echo.
echo Services Running:
echo - Python Server (Port 8000) - Full System
echo - Dashboard (Browser) - Visualization
echo.
echo Features Active:
echo - Simulated Market Data
echo - EDF Trading Logic
echo - Real-time WebSocket
echo - Trading Dashboard
echo.
echo Press any key to exit...
pause >nul

echo.
echo Stopping Python Server...
taskkill /f /im python.exe 2>nul
echo System stopped.
