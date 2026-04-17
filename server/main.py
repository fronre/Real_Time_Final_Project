import asyncio
import socket
import threading
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import json
from typing import List
import time

app = FastAPI(title="Real-time Trading Simulation Server")

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        print(f"🔗 New WebSocket connection. Total: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
        print(f"❌ WebSocket disconnected. Total: {len(self.active_connections)}")

    async def broadcast(self, message: str):
        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except:
                disconnected.append(connection)
        
        # Remove dead connections
        for conn in disconnected:
            self.disconnect(conn)

manager = ConnectionManager()

class MarketData(BaseModel):
    symbol: str
    price: float
    balance: float
    volume: int
    timestamp: int

def parse_market_data(data_string: str) -> MarketData:
    """Parse market data from C bot format: 'symbol:price:balance:volume:timestamp'"""
    parts = data_string.strip().split(':')
    if len(parts) != 5:
        raise ValueError(f"Invalid data format: {data_string}")
    
    return MarketData(
        symbol=parts[0],
        price=float(parts[1]),
        balance=float(parts[2]),
        volume=int(parts[3]),
        timestamp=int(parts[4])
    )

async def connect_to_c_bot():
    """Connect to C bot and receive market data"""
    while True:
        try:
            print("🔌 Connecting to C bot...")
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.connect(('localhost', 8080))
            print("✅ Connected to C bot!")
            
            buffer = ""
            while True:
                data = client_socket.recv(1024).decode('utf-8')
                if not data:
                    break
                
                buffer += data
                while '\n' in buffer:
                    line, buffer = buffer.split('\n', 1)
                    if line.strip():
                        try:
                            market_data = parse_market_data(line)
                            # Broadcast to all WebSocket clients
                            await manager.broadcast(market_data.json())
                            print(f"📊 Received and broadcasted: {market_data.symbol} ${market_data.price}")
                        except ValueError as e:
                            print(f"⚠️  Error parsing data: {e}")
                
                await asyncio.sleep(0.01)  # Small delay to prevent blocking
                
        except Exception as e:
            print(f"❌ Connection error: {e}")
            print("🔄 Reconnecting in 3 seconds...")
            await asyncio.sleep(3)

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()  # Keep connection alive
    except WebSocketDisconnect:
        manager.disconnect(websocket)

@app.get("/")
async def get():
    return {"message": "Real-time Trading Simulation Server", "status": "running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "connections": len(manager.active_connections)}

@app.on_event("startup")
async def startup_event():
    """Start the C bot connection when server starts"""
    print("🚀 Starting FastAPI server...")
    print("🔌 Starting C bot connection in background...")
    # Start the C bot connection in background
    asyncio.create_task(connect_to_c_bot())

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
