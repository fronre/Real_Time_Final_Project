#!/bin/bash

echo "========================================"
echo "   Real-Time Trading System Launcher"
echo "========================================"
echo

echo "[1/3] Starting Python Server..."
cd server
gnome-terminal -- python main.py &
sleep 3

echo "[2/3] Starting C Bot..."
cd ../bot
gnome-terminal -- ./market_bot &
sleep 2

echo "[3/3] Opening Dashboard..."
cd ../frontend
xdg-open index.html &

echo
echo "========================================"
echo "   System Started Successfully!"
echo "========================================"
echo
echo "Dashboard: http://localhost:8000"
echo "API Status: http://localhost:8000/health"
echo
echo "Press Ctrl+C to stop all services..."
wait
