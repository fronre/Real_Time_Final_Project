@echo off
echo ========================================
echo    Real-Time Trading System Launcher
echo ========================================
echo.

echo [1/3] Starting Python Server...
cd server
start "Python Server" cmd /k "python main.py"
timeout /t 3 /nobreak >nul

echo [2/3] Starting C Bot...
cd ..\bot
start "C Bot" cmd /k "market_bot.exe"
timeout /t 2 /nobreak >nul

echo [3/3] Opening Dashboard...
cd ..\frontend
start index.html

echo.
echo ========================================
echo    System Started Successfully!
echo ========================================
echo.
echo Dashboard: http://localhost:8000
echo API Status: http://localhost:8000/health
echo.
echo Press any key to exit...
pause >nul
