#!/bin/bash

# Stop script for Real-Time Trading Simulation System

echo "🛑 Stopping Real-Time Trading System..."
echo "======================================"

# Kill C bot
echo "🤖 Stopping C Bot..."
pkill -f market_bot
if [ $? -eq 0 ]; then
    echo "✅ C Bot stopped"
else
    echo "ℹ️  C Bot was not running"
fi

# Kill Python server
echo "🐍 Stopping Python Server..."
pkill -f "python.*main.py"
if [ $? -eq 0 ]; then
    echo "✅ Python Server stopped"
else
    echo "ℹ️  Python Server was not running"
fi

# Additional cleanup
echo "🧹 Additional cleanup..."
pkill -f "uvicorn" 2>/dev/null

echo ""
echo "✅ All services stopped successfully!"
echo "🔌 Ports 8080 and 8000 should now be available"
