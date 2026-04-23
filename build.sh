#!/bin/bash

echo "========================================"
echo "   Building Trading System"
echo "========================================"
echo

echo "[1/2] Building C Bot..."
cd bot
gcc -Wall -Wextra -std=c99 -o market_bot market_bot.c -lpthread
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to build C bot"
    exit 1
fi
echo "C Bot built successfully!"

echo "[2/2] Installing Python dependencies..."
cd ../server
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to install Python dependencies"
    exit 1
fi
echo "Python dependencies installed!"

echo
echo "========================================"
echo "   Build Complete!"
echo "========================================"
echo
echo "Now run: ./start.sh"
echo
