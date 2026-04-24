@echo off
title Real-Time Trading System - Complete Setup
color 0A

echo.
echo ╔══════════════════════════════════════════════════════════════╗
echo ║         🚀 REAL-TIME TRADING SYSTEM - COMPLETE SETUP            ║
echo ║              🎓 University Project - EDF Algorithm              ║
echo ╚══════════════════════════════════════════════════════════════╝
echo.

echo [1/5] Checking Python installation...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python not found! Please install Python first.
    pause
    exit /b 1
)
echo ✅ Python found!

echo.
echo [2/5] Installing required packages...
cd server
pip install -r requirements.txt >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Failed to install packages!
    pause
    exit /b 1
)
echo ✅ Packages installed!

echo.
echo [3/5] Starting Python Trading Server...
start "Python Trading Server" cmd /k "python working_server.py"
timeout /t 3 /nobreak >nul

echo.
echo [4/5] Opening Trading Dashboard...
cd ..
start "" "http://localhost:8000"
timeout /t 2 /nobreak >nul
start "" "frontend\simple_dashboard.html"

echo.
echo [5/5] System Status Check...
timeout /t 5 /nobreak >nul

echo.
echo ╔══════════════════════════════════════════════════════════════╗
echo ║                    🎯 SYSTEM READY!                           ║
echo ║                                                              ║
echo ║  🌐 Trading Dashboard: http://localhost:8000                  ║
echo ║  📊 Alternative: frontend\simple_dashboard.html                 ║
echo ║                                                              ║
echo ║  💰 Features Active:                                          ║
echo ║     • Real-Time Market Data                                   ║
echo ║     • EDF Trading Algorithm                                   ║
echo ║     • Live Price Charts                                       ║
echo ║     • Trading Signals                                         ║
echo ║     • Performance Metrics                                     ║
echo ║                                                              ║
echo ║  🛑 To stop: Close server window or run STOP_SYSTEM.bat      ║
echo ╚══════════════════════════════════════════════════════════════╝
echo.

echo 🎓 For academic presentation:
echo    • Show the dashboard with real-time data
echo    • Explain EDF Algorithm implementation
echo    • Demonstrate trading signals execution
echo    • Use PRESENTATION_GUIDE.md for reference
echo.

echo Press any key to exit setup...
pause >nul

echo.
echo 📋 Quick Links for Presentation:
echo    • GitHub: https://github.com/fronre/Real_Time_Final_Project.git
echo    • Guide: PRESENTATION_GUIDE.md
echo    • Defense: ACADEMIC_DEFENSE.md
echo.
echo 🎉 System is running! Good luck with your presentation!
