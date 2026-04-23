import asyncio
import websockets
import json
import random
import time
from datetime import datetime
import threading

# Enhanced trading engine with more dynamic data
class DynamicTradingEngine:
    def __init__(self):
        self.balance = 10000.0
        self.total_pnl = 0.0
        self.trade_count = 0
        self.positions = {}
        self.edf_tasks = []
        self.edf_log = []
        self.task_id = 1
        self.price_history = {}
        self.base_prices = {
            "BTC": 45000, "ETH": 3000, "USDT": 1, 
            "PUBG_UC": 0.01, "COD_POINTS": 0.02
        }
        self.current_prices = self.base_prices.copy()
        self.market_trends = {symbol: 0 for symbol in self.base_prices}
        
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
            # Add to position
            if task["symbol"] not in self.positions:
                self.positions[task["symbol"]] = {"quantity": 0, "avg_price": 0}
            pos = self.positions[task["symbol"]]
            total_cost = pos["quantity"] * pos["avg_price"] + task["price"] * task["quantity"]
            pos["quantity"] += task["quantity"]
            pos["avg_price"] = total_cost / pos["quantity"]
        else:
            if task["symbol"] in self.positions:
                pos = self.positions[task["symbol"]]
                sell_quantity = min(task["quantity"], pos["quantity"])
                self.balance += task["price"] * sell_quantity
                pos["quantity"] -= sell_quantity
                if pos["quantity"] == 0:
                    del self.positions[task["symbol"]]
            
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
        """Update market prices with realistic movements"""
        for symbol in self.base_prices:
            # Create realistic price movements
            base_price = self.base_prices[symbol]
            
            # Update trend (random walk)
            self.market_trends[symbol] += random.uniform(-0.02, 0.02)
            self.market_trends[symbol] = max(-0.1, min(0.1, self.market_trends[symbol]))
            
            # Calculate new price
            trend_factor = 1 + self.market_trends[symbol]
            volatility = 0.02 if symbol == "USDT" else 0.08
            random_factor = 1 + random.uniform(-volatility, volatility)
            
            new_price = base_price * trend_factor * random_factor
            
            # Keep price within reasonable bounds
            min_price = base_price * 0.5
            max_price = base_price * 2.0
            self.current_prices[symbol] = max(min_price, min(max_price, new_price))

# Global trading engine
trading_engine = DynamicTradingEngine()

async def handle_websocket(websocket, path):
    """Handle WebSocket connections"""
    print(f"🔌 New client connected: {websocket.remote_address}")
    
    try:
        update_counter = 0
        while True:
            update_counter += 1
            
            # Update market prices
            trading_engine.update_market_prices()
            
            # Pick a symbol to display (rotate through them)
            symbols = list(trading_engine.base_prices.keys())
            symbol = symbols[update_counter % len(symbols)]
            
            current_time = time.time()
            timestamp_sec = int(current_time)
            timestamp_usec = int((current_time - timestamp_sec) * 1000000)
            
            current_price = trading_engine.current_prices[symbol]
            
            # Update price history
            if symbol not in trading_engine.price_history:
                trading_engine.price_history[symbol] = []
            trading_engine.price_history[symbol].append(current_price)
            if len(trading_engine.price_history[symbol]) > 50:
                trading_engine.price_history[symbol].pop(0)
            
            # Create market data
            market_data = {
                "type": "market_data",
                "data": {
                    "symbol": symbol,
                    "price": current_price,
                    "balance": trading_engine.balance,
                    "volume": random.randint(1000, 50000),
                    "timestamp_sec": timestamp_sec,
                    "timestamp_usec": timestamp_usec,
                    "volatility": 0.08 if symbol != "USDT" else 0.01,
                    "trend": trading_engine.market_trends[symbol]
                },
                "trading_stats": {
                    "balance": trading_engine.balance,
                    "total_pnl": trading_engine.total_pnl,
                    "trade_count": trading_engine.trade_count,
                    "active_positions": len(trading_engine.positions)
                },
                "edf_stats": trading_engine.get_edf_stats()
            }
            
            # Generate and execute EDF tasks more frequently
            if random.random() < 0.5:  # 50% chance to generate task
                trading_engine.generate_edf_task()
            
            if random.random() < 0.6:  # 60% chance to execute task
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
            
            # Debug output
            if update_counter % 5 == 0:  # Print every 5 updates
                print(f"📊 {symbol}: ${current_price:.2f} | Balance: ${trading_engine.balance:.2f} | Trades: {trading_engine.trade_count}")
            
            await asyncio.sleep(0.2)  # 5 updates per second (faster for better visualization)
            
    except websockets.exceptions.ConnectionClosed:
        print(f"❌ Client disconnected: {websocket.remote_address}")
    except Exception as e:
        print(f"🚨 Error: {e}")

async def main():
    """Main server function"""
    print("🚀 Starting DYNAMIC Real-Time Trading Server...")
    print("📍 WebSocket Server: ws://localhost:8000")
    print("📊 Features: Dynamic Prices, EDF Scheduling, Real-time Trading")
    print("⚡ Updates: 5 times per second for smooth visualization")
    print("🌐 Open frontend/index.html in your browser")
    print("-" * 60)
    
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
