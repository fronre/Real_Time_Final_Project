import asyncio
import websockets
import json
import random
import time
from datetime import datetime
import threading

# Simple trading engine without complex dependencies
class SimpleTradingEngine:
    def __init__(self):
        self.balance = 10000.0
        self.total_pnl = 0.0
        self.trade_count = 0
        self.positions = {}
        self.edf_tasks = []
        self.edf_log = []
        self.task_id = 1
        
    def generate_edf_task(self):
        """Generate EDF trading task"""
        task = {
            "id": self.task_id,
            "type": random.choice(["BUY", "SELL"]),
            "symbol": random.choice(["BTC", "ETH", "USDT", "PUBG_UC", "COD_POINTS"]),
            "price": random.uniform(1, 50000),
            "quantity": random.randint(1, 100),
            "deadline": time.time() + random.uniform(0.1, 5.0),
            "created": time.time()
        }
        self.task_id += 1
        self.edf_tasks.append(task)
        
        # Sort by deadline (EDF)
        self.edf_tasks.sort(key=lambda x: x["deadline"])
        
        return task
    
    def execute_next_task(self):
        """Execute next EDF task"""
        if not self.edf_tasks:
            return None
            
        current_time = time.time()
        task = self.edf_tasks[0]
        
        # Check deadline
        if current_time > task["deadline"]:
            # Missed deadline
            self.edf_log.append({
                "timestamp": current_time,
                "event": "MISSED_DEADLINE",
                "task_id": task["id"],
                "symbol": task["symbol"]
            })
            self.edf_tasks.pop(0)
            return {"status": "missed", "task": task}
        
        # Execute task
        self.edf_log.append({
            "timestamp": current_time,
            "event": "EXECUTED",
            "task_id": task["id"],
            "symbol": task["symbol"]
        })
        
        self.trade_count += 1
        if task["type"] == "BUY":
            self.balance -= task["price"] * task["quantity"]
        else:
            self.balance += task["price"] * task["quantity"]
            
        self.edf_tasks.pop(0)
        return {"status": "executed", "task": task}
    
    def get_edf_stats(self):
        """Get EDF performance statistics"""
        total = len(self.edf_log)
        executed = len([log for log in self.edf_log if log["event"] == "EXECUTED"])
        missed = len([log for log in self.edf_log if log["event"] == "MISSED_DEADLINE"])
        
        return {
            "total_tasks": total,
            "executed_tasks": executed,
            "missed_deadlines": missed,
            "success_rate": (executed / total * 100) if total > 0 else 0,
            "queue_size": len(self.edf_tasks)
        }

# Global trading engine
trading_engine = SimpleTradingEngine()

async def handle_websocket(websocket, path):
    """Handle WebSocket connections"""
    print(f"New client connected: {websocket.remote_address}")
    
    try:
        while True:
            # Generate market data
            assets = ["BTC", "ETH", "USDT", "PUBG_UC", "COD_POINTS"]
            symbol = random.choice(assets)
            base_price = {"BTC": 45000, "ETH": 3000, "USDT": 1, "PUBG_UC": 0.01, "COD_POINTS": 0.02}
            
            current_time = time.time()
            timestamp_sec = int(current_time)
            timestamp_usec = int((current_time - timestamp_sec) * 1000000)
            
            market_data = {
                "type": "market_data",
                "data": {
                    "symbol": symbol,
                    "price": base_price[symbol] * random.uniform(0.95, 1.05),
                    "balance": trading_engine.balance,
                    "volume": random.randint(1000, 10000),
                    "timestamp_sec": timestamp_sec,
                    "timestamp_usec": timestamp_usec,
                    "volatility": random.uniform(0.01, 0.2),
                    "trend": random.uniform(-0.1, 0.1)
                },
                "trading_stats": {
                    "balance": trading_engine.balance,
                    "total_pnl": trading_engine.total_pnl,
                    "trade_count": trading_engine.trade_count,
                    "active_positions": len(trading_engine.positions)
                },
                "edf_stats": trading_engine.get_edf_stats()
            }
            
            # Generate and execute EDF tasks
            if random.random() < 0.3:  # 30% chance to generate task
                trading_engine.generate_edf_task()
            
            if random.random() < 0.4:  # 40% chance to execute task
                result = trading_engine.execute_next_task()
                if result:
                    signal_data = {
                        "type": "trading_signal",
                        "data": {
                            "symbol": result["task"]["symbol"],
                            "signal": result["task"]["type"],
                            "price": result["task"]["price"],
                            "quantity": result["task"]["quantity"],
                            "timestamp": timestamp_sec,
                            "reason": f"EDF Task {result['status']}",
                            "confidence": 0.8
                        }
                    }
                    await websocket.send(json.dumps(signal_data))
            
            # Send market data
            await websocket.send(json.dumps(market_data))
            
            await asyncio.sleep(0.1)  # 10 updates per second
            
    except websockets.exceptions.ConnectionClosed:
        print(f"Client disconnected: {websocket.remote_address}")
    except Exception as e:
        print(f"Error: {e}")

async def main():
    """Main server function"""
    print("🚀 Starting Simple Real-Time Trading Server...")
    print("📍 WebSocket Server: ws://localhost:8000")
    print("📊 Features: EDF Scheduling, Real-time Trading, Market Simulation")
    print("🌐 Open frontend/index.html in your browser")
    print("-" * 50)
    
    # Start WebSocket server
    async with websockets.serve(handle_websocket, "localhost", 8000):
        print("✅ Server started successfully!")
        print("⏳ Waiting for connections...")
        await asyncio.Future()  # Run forever

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
