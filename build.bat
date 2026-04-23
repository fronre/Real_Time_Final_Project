@echo off
echo ========================================
echo    Building Trading System
echo ========================================
echo.

echo [1/2] Building C Bot...
cd bot
gcc -Wall -Wextra -std=c99 -o market_bot.exe market_bot.c -lpthread
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Failed to build C bot
    pause
    exit /b 1
)
echo C Bot built successfully!

echo [2/2] Installing Python dependencies...
cd ..\server
pip install -r requirements.txt
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Failed to install Python dependencies
    pause
    exit /b 1
)
echo Python dependencies installed!

echo.
echo ========================================
echo    Build Complete!
echo ========================================
echo.
echo Now run: start.bat
echo.
pause
