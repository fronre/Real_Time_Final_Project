@echo off
echo ========================================
echo   Real-Time Trading System Launcher
echo         (EDF Algorithm v2.0)
echo ========================================
echo.

echo [1/4] Building C Bot with EDF...
cd bot
make
if %errorlevel% neq 0 (
    echo ERROR: Failed to build C bot!
    pause
    exit /b 1
)
echo C Bot built successfully!
timeout /t 2 /nobreak >nul

echo [2/4] Starting C Market Bot (EDF Engine)...
start "C Market Bot" cmd /k "market_bot.exe"
timeout /t 3 /nobreak >nul

echo [3/4] Starting Python FastAPI Server...
cd ..\server
start "Python Server" cmd /k "python main.py"
timeout /t 3 /nobreak >nul

echo [4/4] Opening Trading Dashboard...
cd ..
start "" "http://localhost:8000"
timeout /t 2 /nobreak >nul
start "" "frontend\index.html"

echo.
echo ========================================
echo    EDF Trading System Started!
echo ========================================
echo.
echo Services Running:
echo - C Bot (Port 8080) - Market Data + EDF Engine
echo - Python Server (Port 8000) - Trading Logic + WebSocket
echo - Dashboard (Browser) - Real-time Visualization
echo.
echo Features Active:
echo - Earliest Deadline First (EDF) Scheduling
echo - Microsecond Precision Timing
echo - Real-time Task Execution
echo - Deadline Monitoring
echo - Trading Performance Metrics
echo.
echo API Endpoints:
echo - Health: http://localhost:8000/health
echo - EDF Stats: http://localhost:8000/edf-stats
echo - Positions: http://localhost:8000/positions
echo.
echo You should see:
echo - Live market data with microsecond timestamps
echo - EDF task queue management
echo - Real-time trading signals
echo - Deadline execution monitoring
echo - Success rate statistics
echo.
echo Press any key to exit...
pause >nul

echo.
echo Stopping system...
taskkill /f /im market_bot.exe 2>nul
taskkill /f /im python.exe 2>nul
echo System stopped.
