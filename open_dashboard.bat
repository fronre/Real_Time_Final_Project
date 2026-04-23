@echo off
echo ========================================
echo    Opening Real-Time Trading Dashboard
echo ========================================
echo.

echo [1/2] Testing server connection...
curl -s http://localhost:8001/health > nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Server not running on http://localhost:8001
    echo Please start the server first:
    echo   cd server
    echo   python realtime_trading_engine.py
    pause
    exit /b 1
)

echo [2/2] Opening dashboard...
start "" "http://localhost:8001/api/market-data"
timeout /t 2 /nobreak >nul
start "" "c:\Users\pc gamer\Desktop\Real_Time_Final_Project\frontend\realtime_dashboard.html"

echo.
echo ========================================
echo    Dashboard opened successfully!
echo ========================================
echo.
echo Server: http://localhost:8001
echo Dashboard: realtime_dashboard.html
echo.
echo You should see:
echo - Live trading data
echo - EDF scheduling in action
echo - Real-time P&L updates
echo - Active positions
echo.
pause
