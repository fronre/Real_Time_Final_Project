# ========================================
# Real-Time Trading System Launcher
#         (PowerShell Version)
# ========================================

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Real-Time Trading System Launcher" -ForegroundColor Yellow
Write-Host "        (EDF Algorithm v2.0)" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Step 1: Check GCC
Write-Host "[1/4] Checking GCC compiler..." -ForegroundColor Blue
try {
    gcc --version | Select-Object -First 1
    Write-Host "✅ GCC found!" -ForegroundColor Green
} catch {
    Write-Host "❌ GCC not found! Please run INSTALL_COMPILER.bat first" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

# Step 2: Build C Bot
Write-Host "[2/4] Building C Bot with EDF..." -ForegroundColor Blue
Set-Location bot
try {
    make
    if ($LASTEXITCODE -ne 0) { throw "Build failed" }
    Write-Host "✅ C Bot built successfully!" -ForegroundColor Green
} catch {
    Write-Host "❌ Build failed! Please check your GCC installation." -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

# Step 3: Start C Bot
Write-Host "[3/4] Starting C Market Bot (EDF Engine)..." -ForegroundColor Blue
Start-Process -FilePath "cmd.exe" -ArgumentList "/k", "market_bot.exe" -WindowStyle Normal
Write-Host "✅ C Bot started!" -ForegroundColor Green
Start-Sleep -Seconds 3

# Step 4: Start Python Server
Write-Host "[4/4] Starting Python FastAPI Server..." -ForegroundColor Blue
Set-Location ..\server
Start-Process -FilePath "cmd.exe" -ArgumentList "/k", "python main.py" -WindowStyle Normal
Write-Host "✅ Python Server started!" -ForegroundColor Green
Start-Sleep -Seconds 3

# Step 5: Open Dashboard
Write-Host "Opening Trading Dashboard..." -ForegroundColor Blue
Set-Location ..
Start-Process "http://localhost:8000"
Start-Sleep -Seconds 2
Start-Process "frontend\index.html"

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "    EDF Trading System Started!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Services Running:" -ForegroundColor Yellow
Write-Host "- C Bot (Port 8080) - Market Data + EDF Engine" -ForegroundColor White
Write-Host "- Python Server (Port 8000) - Trading Logic + WebSocket" -ForegroundColor White
Write-Host "- Dashboard (Browser) - Real-time Visualization" -ForegroundColor White
Write-Host ""
Write-Host "Features Active:" -ForegroundColor Yellow
Write-Host "- Earliest Deadline First (EDF) Scheduling" -ForegroundColor White
Write-Host "- Microsecond Precision Timing" -ForegroundColor White
Write-Host "- Real-time Task Execution" -ForegroundColor White
Write-Host "- Deadline Monitoring" -ForegroundColor White
Write-Host "- Trading Performance Metrics" -ForegroundColor White
Write-Host ""
Write-Host "API Endpoints:" -ForegroundColor Yellow
Write-Host "- Health: http://localhost:8000/health" -ForegroundColor White
Write-Host "- EDF Stats: http://localhost:8000/edf-stats" -ForegroundColor White
Write-Host "- Positions: http://localhost:8000/positions" -ForegroundColor White
Write-Host ""
Write-Host "Press Enter to stop all services..." -ForegroundColor Cyan
Read-Host

# Stop services
Write-Host ""
Write-Host "Stopping system..." -ForegroundColor Red
Stop-Process -Name "market_bot" -Force -ErrorAction SilentlyContinue
Stop-Process -Name "python" -Force -ErrorAction SilentlyContinue
Write-Host "✅ System stopped!" -ForegroundColor Green
