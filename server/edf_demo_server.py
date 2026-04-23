import asyncio
import websockets
import json
import random
import time

class EDFDemoEngine:
    def __init__(self):
        self.balance = 10000.0
        self.total_pnl = 0.0
        self.trade_count = 0
        self.edf_tasks = []
        self.edf_log = []
        self.task_id = 1
        self.executed_count = 0
        self.missed_count = 0
        
    def generate_edf_task(self):
        """Generate EDF trading task with clear deadline"""
        task = {
            "id": self.task_id,
            "type": random.choice(["BUY", "SELL"]),
            "symbol": random.choice(["BTC", "ETH", "USDT"]),
            "price": random.uniform(100, 50000),
            "quantity": random.randint(1, 50),
            "deadline": time.time() + random.uniform(1.0, 10.0),  # 1-10 seconds
            "created": time.time()
        }
        self.task_id += 1
        self.edf_tasks.append(task)
        
        # Sort by EDF - earliest deadline first
        self.edf_tasks.sort(key=lambda x: x["deadline"])
        
        print(f"📋 Task #{task['id']} Created: {task['type']} {task['symbol']} (Deadline: {task['deadline'] - time.time():.1f}s)")
        return task
    
    def execute_next_task(self):
        """Execute next EDF task with deadline checking"""
        if not self.edf_tasks:
            return None
            
        current_time = time.time()
        task = self.edf_tasks[0]  # First task = earliest deadline (EDF)
        
        # Check if deadline missed
        if current_time > task["deadline"]:
            self.missed_count += 1
            self.edf_log.append({
                "timestamp": current_time,
                "event": "MISSED_DEADLINE",
                "task_id": task["id"],
                "symbol": task["symbol"],
                "deadline": task["deadline"],
                "missed_by": current_time - task["deadline"]
            })
            
            print(f"🚨 MISSED DEADLINE: Task #{task['id']} - {task['type']} {task['symbol']} (Late by {current_time - task['deadline']:.1f}s)")
            
            self.edf_tasks.pop(0)
            return {"status": "missed", "task": task}
        
        # Execute task before deadline
        self.executed_count += 1
        self.trade_count += 1
        execution_time = current_time - task["deadline"]
        
        self.edf_log.append({
            "timestamp": current_time,
            "event": "EXECUTED",
            "task_id": task["id"],
            "symbol": task["symbol"],
            "deadline": task["deadline"],
            "executed_early": task["deadline"] - current_time
        })
        
        print(f"✅ EXECUTED: Task #{task['id']} - {task['type']} {task['symbol']} (Early by {task['deadline'] - current_time:.1f}s)")
        
        # Update balance
        if task["type"] == "BUY":
            self.balance -= task["price"] * task["quantity"]
        else:
            self.balance += task["price"] * task["quantity"]
        
        self.edf_tasks.pop(0)
        return {"status": "executed", "task": task}
    
    def get_edf_stats(self):
        """Get EDF performance statistics"""
        total_tasks = self.executed_count + self.missed_count
        success_rate = (self.executed_count / total_tasks * 100) if total_tasks > 0 else 0
        
        return {
            "total_tasks": total_tasks,
            "executed_tasks": self.executed_count,
            "missed_deadlines": self.missed_count,
            "success_rate": success_rate,
            "queue_size": len(self.edf_tasks),
            "next_deadline": self.edf_tasks[0]["deadline"] if self.edf_tasks else None
        }

trading_engine = EDFDemoEngine()

async def handle_websocket(websocket, path):
    """Handle WebSocket connections with EDF demo"""
    print(f"🔌 EDF Demo Client connected: {websocket.remote_address}")
    
    try:
        update_counter = 0
        while True:
            update_counter += 1
            
            current_time = time.time()
            timestamp_sec = int(current_time)
            timestamp_usec = int((current_time - timestamp_sec) * 1000000)
            
            # Generate EDF tasks frequently
            if random.random() < 0.4:  # 40% chance
                trading_engine.generate_edf_task()
            
            # Execute EDF tasks
            if random.random() < 0.6:  # 60% chance
                result = trading_engine.execute_next_task()
                if result:
                    signal_data = {
                        "type": "edf_event",
                        "data": {
                            "event_type": result["status"],
                            "task_id": result["task"]["id"],
                            "symbol": result["task"]["symbol"],
                            "task_type": result["task"]["type"],
                            "price": result["task"]["price"],
                            "quantity": result["task"]["quantity"],
                            "timestamp": timestamp_sec,
                            "reason": f"EDF Task {result['status']}"
                        }
                    }
                    await websocket.send(json.dumps(signal_data))
            
            # Send market data with EDF stats
            market_data = {
                "type": "market_data",
                "data": {
                    "symbol": random.choice(["BTC", "ETH", "USDT"]),
                    "price": random.uniform(100, 50000),
                    "balance": trading_engine.balance,
                    "volume": random.randint(1000, 10000),
                    "timestamp_sec": timestamp_sec,
                    "timestamp_usec": timestamp_usec,
                    "volatility": 0.02,
                    "trend": random.uniform(-0.05, 0.05)
                },
                "trading_stats": {
                    "balance": trading_engine.balance,
                    "total_pnl": trading_engine.total_pnl,
                    "trade_count": trading_engine.trade_count,
                    "active_positions": len(trading_engine.edf_tasks)
                },
                "edf_stats": trading_engine.get_edf_stats()
            }
            
            await websocket.send(json.dumps(market_data))
            
            # Print EDF status every 5 updates
            if update_counter % 5 == 0:
                stats = trading_engine.get_edf_stats()
                print(f"📊 EDF Status: {stats['executed_tasks']}/{stats['total_tasks']} executed ({stats['success_rate']:.1f}%) | Queue: {stats['queue_size']}")
            
            await asyncio.sleep(1.0)  # 1 update per second for clarity
            
    except websockets.exceptions.ConnectionClosed:
        print(f"❌ Client disconnected: {websocket.remote_address}")
    except Exception as e:
        print(f"🚨 Error: {e}")

async def main():
    """Main EDF demo server"""
    print("🎯 Starting EDF Algorithm Demo Server...")
    print("📍 WebSocket Server: ws://localhost:8000")
    print("📊 Features: Clear EDF Scheduling, Deadline Monitoring")
    print("🌐 Open frontend/candlestick_dashboard.html")
    print("⏰ Watch console for EDF events!")
    print("-" * 60)
    
    async with websockets.serve(handle_websocket, "localhost", 8000):
        print("✅ EDF Demo Server started!")
        print("⏳ Generating and executing EDF tasks...")
        await asyncio.Future()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 EDF Demo stopped by user")
