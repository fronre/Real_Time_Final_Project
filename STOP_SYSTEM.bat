@echo off
echo ========================================
echo     Stop Real-Time Trading System
echo ========================================
echo.

echo Stopping C Market Bot...
taskkill /f /im market_bot.exe 2>nul
echo C Bot stopped.

echo Stopping Python Server...
taskkill /f /im python.exe 2>nul
echo Python Server stopped.

echo.
echo All services stopped successfully!
echo.
pause
