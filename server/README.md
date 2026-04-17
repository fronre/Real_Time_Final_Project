# Trading Server (Python FastAPI)

A FastAPI server that receives market data from the C bot and broadcasts it via WebSockets.

## Features

- Receives market data from C bot via TCP socket (localhost:8080)
- Broadcasts data to WebSocket clients
- Health check endpoint
- Connection management

## Setup & Run

```bash
# Install dependencies
pip install -r requirements.txt

# Run the server
python main.py
```

The server will:
1. Start on http://localhost:8000
2. Automatically connect to C bot
3. Listen for WebSocket connections on /ws
4. Broadcast market data to connected clients

## API Endpoints

- `GET /` - Server status
- `GET /health` - Health check with connection count
- `WebSocket /ws` - Real-time market data stream

## Data Format

The server receives data in format: `symbol:price:balance:volume:timestamp`
And broadcasts JSON to WebSocket clients:

```json
{
  "symbol": "AAPL",
  "price": 102.34,
  "balance": 10500.50,
  "volume": 5678,
  "timestamp": 1714321234
}
```
