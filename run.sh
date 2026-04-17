#!/bin/bash

# Real-Time Trading Simulation System - Quick Start Script
# This script helps you run all components in the correct order

echo "🚀 Real-Time Trading Simulation System"
echo "======================================"

# Function to check if a port is in use
check_port() {
    local port=$1
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
        echo "⚠️  Port $port is already in use"
        return 1
    fi
    return 0
}

# Function to kill existing processes
cleanup() {
    echo "🧹 Cleaning up existing processes..."
    pkill -f market_bot 2>/dev/null
    pkill -f "python.*main.py" 2>/dev/null
    sleep 2
}

# Check dependencies
echo "🔍 Checking dependencies..."
if ! command -v gcc &> /dev/null; then
    echo "❌ GCC is not installed. Please install build-essential."
    exit 1
fi

if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed."
    exit 1
fi

# Cleanup existing processes
cleanup

# Check ports
if ! check_port 8080; then
    echo "❌ Port 8080 is busy. Please stop the process using it."
    exit 1
fi

if ! check_port 8000; then
    echo "❌ Port 8000 is busy. Please stop the process using it."
    exit 1
fi

echo "✅ Dependencies and ports checked"

# Build C bot
echo "🔨 Building C bot..."
cd bot
make
if [ $? -ne 0 ]; then
    echo "❌ Failed to build C bot"
    exit 1
fi
echo "✅ C bot built successfully"
cd ..

# Install Python dependencies
echo "📦 Installing Python dependencies..."
cd server
pip3 install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "❌ Failed to install Python dependencies"
    exit 1
fi
echo "✅ Python dependencies installed"
cd ..

echo ""
echo "🎯 Starting the system..."
echo "=========================="
echo ""
echo "1️⃣  Starting C Bot (Market Data Generator)..."
echo "   📍 Location: ./bot/market_bot"
echo "   🔌 Port: 8080"
echo ""

# Start C bot in background
cd bot
./market_bot &
BOT_PID=$!
cd ..

# Wait a moment for bot to start
sleep 2

echo "2️⃣  Starting Python Server (FastAPI + WebSocket)..."
echo "   📍 Location: ./server/main.py"
echo "   🌐 HTTP: http://localhost:8000"
echo "   🔌 WebSocket: ws://localhost:8000/ws"
echo ""

# Start Python server in background
cd server
python3 main.py &
SERVER_PID=$!
cd ..

# Wait a moment for server to start
sleep 3

echo "3️⃣  Opening Frontend Dashboard..."
echo "   📍 Location: ./frontend/index.html"
echo ""

# Open frontend (try different commands based on OS)
if command -v xdg-open &> /dev/null; then
    xdg-open frontend/index.html
elif command -v open &> /dev/null; then
    open frontend/index.html
elif command -v start &> /dev/null; then
    start frontend/index.html
else
    echo "📂 Please open frontend/index.html in your browser manually"
fi

echo ""
echo "✅ System is running!"
echo "====================="
echo ""
echo "📊 Dashboard should open in your browser"
echo "🔍 You should see real-time market data updating every second"
echo ""
echo "🛑 To stop the system:"
echo "   Press Ctrl+C or run: ./stop.sh"
echo ""
echo "📝 Logs:"
echo "   C Bot: Check terminal for market data generation"
echo "   Server: Check terminal for WebSocket connections"
echo ""

# Wait for user interrupt
trap 'cleanup; exit 0' INT
echo "Press Ctrl+C to stop all services..."
wait
