import asyncio
import socket
import threading
import json
from typing import List
import time
import logging

logging.basicConfig(level=logging.INFO)

class SimpleWebSocketServer:
    def __init__(self):
        self.clients = []
        self.market_data = []
        
    async def handle_client(self, reader, writer):
        addr = writer.get_extra_info('peername')
        logging.info(f"New client connected: {addr}")
        
        try:
            # Send initial data
            welcome_msg = {
                "type": "welcome",
                "message": "Connected to Trading System",
                "timestamp": time.time()
            }
            writer.write((json.dumps(welcome_msg) + "\n").encode())
            await writer.drain()
            
            while True:
                data = await reader.read(1024)
                if not data:
                    break
                    
                # Keep connection alive
                writer.write(b'pong\n')
                await writer.drain()
                
        except Exception as e:
            logging.error(f"Client error: {e}")
        finally:
            writer.close()
            logging.info(f"Client disconnected: {addr}")
    
    async def start_server(self):
        server = await asyncio.start_server(
            self.handle_client, '0.0.0.0', 8000
        )
        
        logging.info("🚀 Simple Trading Server started on http://localhost:8000")
        
        async with server:
            await server.serve_forever()

class MarketDataGenerator:
    def __init__(self):
        self.assets = [
            {"symbol": "BTC", "price": 45000.0, "volatility": 0.08},
            {"symbol": "ETH", "price": 3000.0, "volatility": 0.10},
            {"symbol": "USDT", "price": 1.0, "volatility": 0.01},
            {"symbol": "PUBG_UC", "price": 0.01, "volatility": 0.15},
            {"symbol": "COD_POINTS", "price": 0.02, "volatility": 0.12},
            {"symbol": "NETFLIX", "price": 15.0, "volatility": 0.05},
            {"symbol": "SPOTIFY", "price": 10.0, "volatility": 0.04},
            {"symbol": "VPN_PREMIUM", "price": 5.0, "volatility": 0.03},
            {"symbol": "DOMAIN_COM", "price": 25.0, "volatility": 0.06},
            {"symbol": "NFT_ART", "price": 100.0, "volatility": 0.20}
        ]
        self.current_asset = 0
        
    def generate_data(self):
        asset = self.assets[self.current_asset]
        
        # Simulate price change
        change = (time.time() % 200 - 100) / 1000.0
        asset["price"] += change * asset["volatility"]
        
        # Keep price in reasonable range
        if asset["price"] < asset["price"] * 0.5:
            asset["price"] = asset["price"] * 0.5
        elif asset["price"] > asset["price"] * 2.0:
            asset["price"] = asset["price"] * 2.0
            
        self.current_asset = (self.current_asset + 1) % len(self.assets)
        
        return {
            "type": "market_data",
            "data": {
                "symbol": asset["symbol"],
                "price": round(asset["price"], 6),
                "balance": 10000.0 + (time.time() % 5000),
                "volume": int(time.time() % 10000 + 1000),
                "timestamp_sec": int(time.time()),
                "timestamp_usec": int((time.time() % 1) * 1000000),
                "volatility": asset["volatility"],
                "trend": (time.time() % 100) / 100.0
            },
            "trading_stats": {
                "balance": 10000.0,
                "total_pnl": (time.time() % 1000) - 500,
                "trade_count": int(time.time() % 100),
                "active_positions": len([a for a in self.assets if a["price"] > 10])
            }
        }

async def main():
    # Start market data generator
    generator = MarketDataGenerator()
    
    # Start simple web server
    server = SimpleWebSocketServer()
    
    # Background task to generate data
    async def generate_market_data():
        while True:
            await asyncio.sleep(0.1)  # Generate data every 100ms
            data = generator.generate_data()
            logging.info(f"Generated: {data['data']['symbol']} ${data['data']['price']}")
    
    # Run both tasks
    await asyncio.gather(
        server.start_server(),
        generate_market_data()
    )

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Server stopped by user")
