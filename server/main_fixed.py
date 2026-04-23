import asyncio
import socket
import threading
import json
from typing import List
import time
import logging
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse
import threading

logging.basicConfig(level=logging.INFO)

class TradingAPIHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed_path = urlparse(self.path)
        
        if parsed_path.path == '/api/market-data':
            self.send_market_data()
        elif parsed_path.path == '/health':
            self.send_health()
        elif parsed_path.path == '/':
            self.send_cors()
        else:
            self.send_404()
    
    def send_market_data(self):
        # Generate market data
        assets = [
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
        
        current_time = time.time()
        asset_index = int(current_time) % len(assets)
        asset = assets[asset_index]
        
        # Simulate price change
        change = (current_time % 200 - 100) / 1000.0
        price = asset["price"] + change * asset["volatility"]
        
        data = {
            "type": "market_data",
            "data": {
                "symbol": asset["symbol"],
                "price": round(price, 6),
                "balance": 10000.0 + (current_time % 5000),
                "volume": int(current_time % 10000 + 1000),
                "timestamp_sec": int(current_time),
                "timestamp_usec": int((current_time % 1) * 1000000),
                "volatility": asset["volatility"],
                "trend": (current_time % 100) / 100.0
            },
            "trading_stats": {
                "balance": 10000.0,
                "total_pnl": (current_time % 1000) - 500,
                "trade_count": int(current_time % 100),
                "active_positions": len([a for a in assets if price > 10])
            }
        }
        
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())
        
        logging.info(f"Sent data: {asset['symbol']} ${price:.6f}")
    
    def send_health(self):
        health_data = {
            "status": "healthy",
            "timestamp": time.time(),
            "service": "trading-api"
        }
        
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(health_data).encode())
    
    def send_404(self):
        self.send_response(404)
        self.end_headers()
        self.wfile.write(b'Not Found')
    
    def send_cors(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(b'CORS OK')
    
    def log_message(self, format, *args):
        # Disable default logging
        pass

def run_server():
    server = HTTPServer(('localhost', 8001), TradingAPIHandler)
    logging.info("🚀 Trading API Server started on http://localhost:8001")
    logging.info("📊 API endpoints:")
    logging.info("   - GET /api/market-data (market data)")
    logging.info("   - GET /health (health check)")
    logging.info("🌐 Open frontend and it will connect automatically!")
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        logging.info("👋 Server stopped by user")
        server.shutdown()

if __name__ == "__main__":
    run_server()
