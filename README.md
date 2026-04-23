# Real-Time Digital Asset Trading System with EDF Algorithm

A high-frequency trading simulation system for digital assets with **Earliest Deadline First (EDF)** scheduling and **microsecond timing precision**.

**Architecture**: **C → Socket → Python → WebSocket → Browser**

## 🎯 System Features

- **10 Digital Assets**: BTC, ETH, USDT, Gaming currencies, Subscriptions, NFTs
- **EDF Scheduling**: Earliest Deadline First algorithm for real-time task management
- **Microsecond Precision**: High-resolution timing for trading decisions
- **Advanced Trading Logic**: Moving averages, momentum, and threshold strategies
- **Real-Time Visualization**: Live charts, trading signals, and performance metrics

## Architecture Overview

```
┌─────────────┐    TCP     ┌─────────────┐    WebSocket    ┌─────────────┐
│    C Bot    │ ────────►  │  Python     │ ──────────────► │  Browser    │
│ (Market     │    8080    │  FastAPI     │       8000      │  Dashboard  │
│  Generator) │            │  + EDF       │                │  + Charts   │
│  + EDF      │            │  + Trading  │                │             │
└─────────────┘            └─────────────┘                └─────────────┘
```

## Project Structure

```
realtimee/
├── bot/                    # C market data generator
│   ├── market_bot.c       # Main bot source code
│   ├── Makefile           # Build configuration
│   └── README.md          # Bot documentation
├── server/                 # Python FastAPI server
│   ├── main.py            # Server with WebSocket support
│   ├── requirements.txt   # Python dependencies
│   └── README.md          # Server documentation
├── frontend/               # Web dashboard
│   ├── index.html         # Main dashboard page
│   └── README.md          # Frontend documentation
└── README.md              # This file
```

## 🚀 Quick Start

### Option 1: Docker (Recommended for Easy Sharing)

**Perfect for sharing with friends!** No technical setup needed.

#### Prerequisites
- Install Docker Desktop: https://www.docker.com/products/docker-desktop/

#### 3 Commands to Run:
```bash
# 1. Open terminal in project folder
cd Real_Time_Final_Project

# 2. Build and start everything
docker-compose up --build

# 3. Open browser
# Go to: http://localhost:3000
```

That's it! 🎉 The trading dashboard will appear automatically.

### Option 2: Manual Setup (For Development)

#### Prerequisites
- GCC compiler (for C bot)
- Python 3.7+ (for FastAPI server)
- Modern web browser (for frontend)

#### Step 1: Build and Run C Bot
```bash
cd bot
make
./market_bot
```

#### Step 2: Start Python Server
```bash
cd server
pip install -r requirements.txt
python main.py
```

#### Step 3: Open Frontend
```bash
cd frontend
# Open index.html in your browser
open index.html  # macOS
# or
xdg-open index.html  # Linux
# or
start index.html  # Windows
```

## Running Order (Important)

1. **Start C Bot first** - It waits for connections on port 8080
2. **Start Python Server** - It connects to the bot and starts WebSocket server
3. **Open Frontend** - It connects to the WebSocket and displays data

## Data Flow

1. **C Bot** generates market data:
   ```
   AAPL:102.34:10500.50:5678:1714321234
   ```

2. **Python Server** receives and converts to JSON:
   ```json
   {
     "symbol": "AAPL",
     "price": 102.34,
     "balance": 10500.50,
     "volume": 5678,
     "timestamp": 1714321234
   }
   ```

3. **Frontend** displays the data with animations and updates

## Features

### C Bot
- Generates realistic market data
- Price fluctuation simulation
- Balance tracking
- Volume generation
- TCP socket communication

### Python Server
- FastAPI framework
- WebSocket broadcasting
- Automatic reconnection
- Connection management
- Health check endpoints

### Frontend Dashboard
- Real-time price updates
- Price change indicators (green/red)
- Account balance display
- Trading volume monitoring
- Connection status
- Recent updates history
- Responsive design
- Smooth animations

## Testing the Pipeline

### Test C Bot Only
```bash
cd bot
./market_bot
# In another terminal:
telnet localhost 8080
# You should see market data streaming
```

### Test Python Server Health
```bash
curl http://localhost:8000/health
# Returns: {"status": "healthy", "connections": 0}
```

### Test WebSocket Connection
```bash
# Use a WebSocket client like wscat:
npm install -g wscat
wscat -c ws://localhost:8000/ws
# You should see JSON data streaming when bot is connected
```

## Troubleshooting

### Common Issues

1. **"Address already in use"**
   - Kill existing processes: `pkill -f market_bot` or `pkill -f python`
   - Wait a few seconds for ports to be released

2. **"Connection refused"**
   - Ensure C bot is running before starting Python server
   - Check if ports 8080 and 8000 are available

3. **"WebSocket connection failed"**
   - Verify Python server is running
   - Check browser console for errors
   - Ensure no firewall blocking WebSocket connections

4. **"No data displaying"**
   - Check C bot console for "Connected to Python server!"
   - Check Python server console for "Connected to C bot!"
   - Verify browser shows green connection status

### Debug Mode

Enable verbose logging by modifying the Python server:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Performance

- **Latency**: < 50ms end-to-end (C → Browser)
- **Update Rate**: 1 Hz (configurable in C bot)
- **Memory Usage**: < 50MB total
- **CPU Usage**: < 5% on modern systems

## Extensions

You can extend this system by:
- Adding more market data fields
- Implementing multiple symbols
- Adding historical data storage
- Creating trading algorithms
- Adding authentication
- Implementing data persistence

## License

MIT License - feel free to use and modify for your projects.
# -Real-Time-Trading-Dashboard
# -Real-Time-Trading-Dashboard
# -Real-Time-Trading-Dashboard
