import asyncio
import websockets
import json
import random
import time
from datetime import datetime

class StableTradingEngine:
    def __init__(self):
        self.balance = 10000.0
        self.total_pnl = 218.21  # Start with some profit like in the image
        self.trade_count = 18
        self.active_positions = 10
        self.edf_tasks = []
        self.edf_log = []
        self.task_id = 1
        
        # Stable prices like in the image
        self.base_prices = {
            "BTC": 45000, "ETH": 3000, "USDT": 1, 
            "COD_POINTS": 0.02, "DOMAIN_COM": 25.00
        }
        self.current_prices = self.base_prices.copy()
        
    def generate_edf_task(self):
        """Generate EDF trading task"""
        task = {
            "id": self.task_id,
            "type": random.choice(["BUY", "SELL"]),
            "symbol": random.choice(list(self.base_prices.keys())),
            "price": random.uniform(1, 50000),
            "quantity": random.randint(1, 100),
            "deadline": time.time() + random.uniform(0.1, 5.0),
            "created": time.time()
        }
        self.task_id += 1
        self.edf_tasks.append(task)
        self.edf_tasks.sort(key=lambda x: x["deadline"])
        return task
    
    def execute_next_task(self):
        """Execute next EDF task"""
        if not self.edf_tasks:
            return None
            
        current_time = time.time()
        task = self.edf_tasks[0]
        
        if current_time > task["deadline"]:
            self.edf_log.append({
                "timestamp": current_time,
                "event": "MISSED_DEADLINE",
                "task_id": task["id"],
                "symbol": task["symbol"]
            })
            self.edf_tasks.pop(0)
            return {"status": "missed", "task": task}
        
        self.edf_log.append({
            "timestamp": current_time,
            "event": "EXECUTED",
            "task_id": task["id"],
            "symbol": task["symbol"]
        })
        
        self.trade_count += 1
        if task["type"] == "BUY":
            self.balance -= task["price"] * task["quantity"]
            self.active_positions += 1
        else:
            self.balance += task["price"] * task["quantity"]
            self.active_positions = max(0, self.active_positions - 1)
            
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
    
    def update_market_prices(self):
        """Update prices slowly and realistically"""
        for symbol in self.base_prices:
            base_price = self.base_prices[symbol]
            
            # Very small changes for stability
            volatility = 0.005 if symbol == "USDT" else 0.02
            change = random.uniform(-volatility, volatility)
            
            new_price = base_price * (1 + change)
            
            # Keep within reasonable bounds
            min_price = base_price * 0.95
            max_price = base_price * 1.05
            self.current_prices[symbol] = max(min_price, min(max_price, new_price))

trading_engine = StableTradingEngine()

async def handle_websocket(websocket, path):
    """Handle WebSocket connections"""
    print(f"🔌 Client connected: {websocket.remote_address}")
    
    try:
        update_counter = 0
        while True:
            update_counter += 1
            
            # Update prices slowly
            trading_engine.update_market_prices()
            
            # Rotate through symbols
            symbols = list(trading_engine.base_prices.keys())
            symbol = symbols[update_counter % len(symbols)]
            
            current_time = time.time()
            timestamp_sec = int(current_time)
            timestamp_usec = int((current_time - timestamp_sec) * 1000000)
            
            current_price = trading_engine.current_prices[symbol]
            
            # Create market data
            market_data = {
                "type": "market_data",
                "data": {
                    "symbol": symbol,
                    "price": current_price,
                    "balance": trading_engine.balance,
                    "volume": random.randint(1000, 10000),
                    "timestamp_sec": timestamp_sec,
                    "timestamp_usec": timestamp_usec,
                    "volatility": 0.02 if symbol != "USDT" else 0.005,
                    "trend": random.uniform(-0.05, 0.05)
                },
                "trading_stats": {
                    "balance": trading_engine.balance,
                    "total_pnl": trading_engine.total_pnl,
                    "trade_count": trading_engine.trade_count,
                    "active_positions": trading_engine.active_positions
                },
                "edf_stats": trading_engine.get_edf_stats()
            }
            
            # Generate and execute tasks less frequently
            if random.random() < 0.2:  # 20% chance
                trading_engine.generate_edf_task()
            
            if random.random() < 0.3:  # 30% chance
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
            
            # Debug output (less frequent)
            if update_counter % 10 == 0:
                print(f"📊 {symbol}: ${current_price:.2f} | Balance: ${trading_engine.balance:.2f}")
            
            # SLOW UPDATE - Every 2 seconds instead of 200ms
            await asyncio.sleep(2.0)
            
    except websockets.exceptions.ConnectionClosed:
        print(f"❌ Client disconnected: {websocket.remote_address}")
    except Exception as e:
        print(f"🚨 Error: {e}")

async def main():
    """Main server function"""
    print("🐌 Starting SLOW Real-Time Trading Server...")
    print("📍 WebSocket Server: ws://localhost:8000")
    print("⏰ Updates: Every 2 seconds (much slower)")
    print("🌐 Open frontend/fixed_dashboard.html in your browser")
    print("-" * 50)
    
    async with websockets.serve(handle_websocket, "localhost", 8000):
        print("✅ Server started successfully!")
        print("⏳ Waiting for connections...")
        await asyncio.Future()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
