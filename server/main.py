import asyncio
import socket
import threading
import random
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import json
from typing import List
import time
import heapq
from datetime import datetime, timedelta
from enum import Enum
import logging

logging.basicConfig(level=logging.INFO)
app = FastAPI(title="Real-time Digital Asset Trading Simulation Server")

class OrderType(Enum):
    BUY = "BUY"
    SELL = "SELL"

class TradingTask(BaseModel):
    id: int
    type: OrderType
    symbol: str
    price: float
    quantity: int
    deadline_sec: int
    deadline_usec: int
    created_sec: int
    created_usec: int
    priority: int
    executed: int = 0
    executed_sec: int = 0
    executed_usec: int = 0
    missed_deadline: int = 0
    
    def __lt__(self, other):
        if self.deadline_sec != other.deadline_sec:
            return self.deadline_sec < other.deadline_sec
        return self.deadline_usec < other.deadline_usec

class MarketData(BaseModel):
    symbol: str
    price: float
    balance: float
    volume: int
    timestamp_sec: int
    timestamp_usec: int
    volatility: float
    trend: float

class TradingSignal(BaseModel):
    symbol: str
    signal: OrderType
    price: float
    quantity: int
    timestamp: int
    reason: str
    confidence: float

class TradingPosition:
    def __init__(self, symbol: str):
        self.symbol = symbol
        self.quantity = 0
        self.avg_price = 0.0
        self.total_cost = 0.0
        
    def add_position(self, quantity: int, price: float):
        if self.quantity == 0:
            self.avg_price = price
            self.quantity = quantity
            self.total_cost = quantity * price
        else:
            new_quantity = self.quantity + quantity
            self.total_cost += quantity * price
            self.avg_price = self.total_cost / new_quantity
            self.quantity = new_quantity
            
    def reduce_position(self, quantity: int, price: float):
        if quantity > self.quantity:
            quantity = self.quantity
        self.quantity -= quantity
        realized_pnl = quantity * (price - self.avg_price)
        if self.quantity == 0:
            self.total_cost = 0
            self.avg_price = 0
        else:
            self.total_cost = self.quantity * self.avg_price
        return realized_pnl

class TradingEngine:
    def __init__(self):
        self.task_queue = []
        self.positions = {}
        self.price_history = {}
        self.trading_signals = []
        self.balance = 10000.0
        self.total_pnl = 0.0
        self.trade_count = 0
        self.executed_tasks = 0
        self.missed_deadlines = 0
        self.lock = threading.Lock()
        self.edf_log = []
        
    def log_edf_event(self, event_type: str, task: TradingTask, timestamp: float = None):
        """Log EDF events for real-time monitoring"""
        if timestamp is None:
            timestamp = time.time()
        
        log_entry = {
            "timestamp": timestamp,
            "event_type": event_type,
            "task_id": task.id,
            "task_type": task.type.value,
            "symbol": task.symbol,
            "deadline_sec": task.deadline_sec,
            "deadline_usec": task.deadline_usec,
            "executed_sec": task.executed_sec,
            "executed_usec": task.executed_usec,
            "missed_deadline": task.missed_deadline
        }
        
        self.edf_log.append(log_entry)
        
        # Keep only last 100 log entries
        if len(self.edf_log) > 100:
            self.edf_log.pop(0)
            
        if event_type == "EXECUTED":
            logging.info(f"✅ [EDF] EXECUTED: Task #{task.id} - {task.type.value} {task.quantity} {task.symbol} at ${task.price:.6f}")
        elif event_type == "MISSED_DEADLINE":
            logging.warning(f"🚨 [EDF] MISSED DEADLINE: Task #{task.id} - {task.type.value} {task.symbol}")
            self.missed_deadlines += 1
            
    def add_edf_task(self, task: TradingTask):
        """Add task to EDF queue"""
        with self.lock:
            heapq.heappush(self.task_queue, task)
            self.log_edf_event("TASK_ADDED", task)
            logging.info(f"📋 [EDF] Task Added: #{task.id} - {task.type.value} {task.quantity} {task.symbol} (Deadline: {task.deadline_sec}.{task.deadline_usec:06d})")
            
    def get_edf_stats(self):
        """Get EDF performance statistics"""
        with self.lock:
            total_tasks = len(self.edf_log)
            executed = sum(1 for log in self.edf_log if log["event_type"] == "EXECUTED")
            missed = sum(1 for log in self.edf_log if log["event_type"] == "MISSED_DEADLINE")
            
            return {
                "total_tasks": total_tasks,
                "executed_tasks": executed,
                "missed_deadlines": missed,
                "success_rate": (executed / total_tasks * 100) if total_tasks > 0 else 0,
                "queue_size": len(self.task_queue)
            }
            
    def update_price_history(self, symbol: str, price: float, timestamp: int):
        if symbol not in self.price_history:
            self.price_history[symbol] = []
        
        self.price_history[symbol].append({
            'price': price,
            'timestamp': timestamp
        })
        
        if len(self.price_history[symbol]) > 50:
            self.price_history[symbol].pop(0)
            
    def calculate_moving_average(self, symbol: str, period: int = 10):
        if symbol not in self.price_history or len(self.price_history[symbol]) < period:
            return None
            
        recent_prices = [p['price'] for p in self.price_history[symbol][-period:]]
        return sum(recent_prices) / len(recent_prices)
        
    def calculate_momentum(self, symbol: str):
        if symbol not in self.price_history or len(self.price_history[symbol]) < 5:
            return 0.0
            
        recent = self.price_history[symbol][-5:]
        if len(recent) < 2:
            return 0.0
            
        price_change = recent[-1]['price'] - recent[0]['price']
        return price_change / recent[0]['price'] if recent[0]['price'] > 0 else 0.0
        
    def generate_trading_signal(self, market_data: MarketData) -> TradingSignal:
        """Generate trading signal using EDF-based logic"""
        symbol = market_data.symbol
        current_price = market_data.price
        
        self.update_price_history(symbol, current_price, market_data.timestamp_sec)
        
        # EDF-based trading: Check if we have urgent tasks for this asset
        urgent_tasks = [task for task in self.task_queue[:5] if task.symbol == symbol and task.type == OrderType.BUY]
        
        signal_type = None
        reason = ""
        confidence = 0.0
        quantity = max(1, int(100 / current_price))
        
        # Priority to assets with urgent EDF tasks
        if urgent_tasks:
            signal_type = OrderType.BUY
            reason = f"Urgent EDF tasks detected for {symbol}"
            confidence = 0.8
        else:
            # Fallback to technical analysis
            ma = self.calculate_moving_average(symbol)
            momentum = self.calculate_momentum(symbol)
            
            if ma and current_price < ma * 0.98 and momentum < -0.02:
                signal_type = OrderType.BUY
                reason = f"Price below MA ({ma:.6f}) with negative momentum"
                confidence = min(0.9, abs(momentum) + abs((ma - current_price) / ma))
            elif ma and current_price > ma * 1.02 and momentum > 0.02:
                signal_type = OrderType.SELL
                reason = f"Price above MA ({ma:.6f}) with positive momentum"
                confidence = min(0.9, abs(momentum) + abs((current_price - ma) / ma))
                
        if signal_type and confidence > 0.5:
            return TradingSignal(
                symbol=symbol,
                signal=signal_type,
                price=current_price,
                quantity=quantity,
                timestamp=market_data.timestamp_sec,
                reason=reason,
                confidence=confidence
            )
        
        return None
        
    def execute_trade(self, signal: TradingSignal):
        with self.lock:
            if signal.symbol not in self.positions:
                self.positions[signal.symbol] = TradingPosition(signal.symbol)
                
            position = self.positions[signal.symbol]
            trade_cost = signal.price * signal.quantity
            
            if signal.signal == OrderType.BUY:
                if self.balance >= trade_cost:
                    position.add_position(signal.quantity, signal.price)
                    self.balance -= trade_cost
                    self.trade_count += 1
                    logging.info(f"EXECUTED BUY: {signal.quantity} {signal.symbol} at ${signal.price:.6f}")
                    return True
            else:
                if position.quantity >= signal.quantity:
                    pnl = position.reduce_position(signal.quantity, signal.price)
                    self.balance += trade_cost
                    self.total_pnl += pnl
                    self.trade_count += 1
                    logging.info(f"EXECUTED SELL: {signal.quantity} {signal.symbol} at ${signal.price:.6f}, PnL: ${pnl:.2f}")
                    return True
                    
        return False

trading_engine = TradingEngine()

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logging.info(f"New WebSocket connection. Total: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
            logging.info(f"WebSocket disconnected. Total: {len(self.active_connections)}")

    async def broadcast(self, message: str):
        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except:
                disconnected.append(connection)
        
        for conn in disconnected:
            self.disconnect(conn)

manager = ConnectionManager()

def parse_market_data(data_string: str) -> MarketData:
    """Parse enhanced market data from C bot format: 'symbol:price:balance:volume:timestamp_sec:timestamp_usec:volatility:trend'"""
    parts = data_string.strip().split(':')
    if len(parts) != 8:
        raise ValueError(f"Invalid data format: {data_string}")
    
    return MarketData(
        symbol=parts[0],
        price=float(parts[1]),
        balance=float(parts[2]),
        volume=int(parts[3]),
        timestamp_sec=int(parts[4]),
        timestamp_usec=int(parts[5]),
        volatility=float(parts[6]),
        trend=float(parts[7])
    )

async def simulate_market_data():
    """Simulate market data when C bot is not available"""
    assets = ["BTC", "ETH", "USDT", "PUBG_UC", "COD_POINTS", "NETFLIX", "SPOTIFY", "VPN_PREMIUM", "DOMAIN_COM", "NFT_ART"]
    base_prices = [45000, 3000, 1, 0.01, 0.02, 15, 10, 5, 25, 100]
    volatilities = [0.08, 0.10, 0.01, 0.15, 0.12, 0.05, 0.04, 0.03, 0.06, 0.20]
    
    asset_data = dict(zip(assets, zip(base_prices, volatilities)))
    current_prices = dict(zip(assets, base_prices))
    
    while True:
        # Generate random market data
        symbol = random.choice(assets)
        base_price, volatility = asset_data[symbol]
        
        # Simulate price movement
        price_change = (random.random() - 0.5) * 2 * volatility * base_price
        current_prices[symbol] = max(base_price * 0.5, min(base_price * 2, current_prices[symbol] + price_change))
        
        # Create market data
        current_time = time.time()
        timestamp_sec = int(current_time)
        timestamp_usec = int((current_time - timestamp_sec) * 1000000)
        
        market_data = MarketData(
            symbol=symbol,
            price=current_prices[symbol],
            balance=10000 + random.random() * 5000,
            volume=random.randint(1000, 10000),
            timestamp_sec=timestamp_sec,
            timestamp_usec=timestamp_usec,
            volatility=volatility,
            trend=random.random()
        )
        
        # Process trading signal
        signal = trading_engine.generate_trading_signal(market_data)
        if signal:
            success = trading_engine.execute_trade(signal)
            if success:
                signal_data = {
                    "type": "trading_signal",
                    "data": signal.dict()
                }
                await manager.broadcast(json.dumps(signal_data))
        
        # Broadcast market data
        enhanced_data = {
            "type": "market_data",
            "data": market_data.dict(),
            "trading_stats": {
                "balance": trading_engine.balance,
                "total_pnl": trading_engine.total_pnl,
                "trade_count": trading_engine.trade_count,
                "active_positions": len(trading_engine.positions)
            },
            "edf_stats": trading_engine.get_edf_stats()
        }
        
        await manager.broadcast(json.dumps(enhanced_data))
        logging.info(f"Simulated: {market_data.symbol} ${market_data.price:.6f}")
        
        await asyncio.sleep(0.1)  # 10 updates per second

async def connect_to_c_bot():
    """Connect to C bot and receive enhanced market data"""
    while True:
        try:
            logging.info("Connecting to C bot...")
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.connect(('localhost', 8080))
            logging.info("Connected to C bot!")
            
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
                            
                            signal = trading_engine.generate_trading_signal(market_data)
                            if signal:
                                success = trading_engine.execute_trade(signal)
                                if success:
                                    signal_data = {
                                        "type": "trading_signal",
                                        "data": signal.dict()
                                    }
                                    await manager.broadcast(json.dumps(signal_data))
                            
                            enhanced_data = {
                                "type": "market_data",
                                "data": market_data.dict(),
                                "trading_stats": {
                                    "balance": trading_engine.balance,
                                    "total_pnl": trading_engine.total_pnl,
                                    "trade_count": trading_engine.trade_count,
                                    "active_positions": len(trading_engine.positions)
                                }
                            }
                            
                            await manager.broadcast(json.dumps(enhanced_data))
                            logging.info(f"Processed: {market_data.symbol} ${market_data.price:.6f}")
                            
                        except ValueError as e:
                            logging.error(f"Error parsing data: {e}")
                
                await asyncio.sleep(0.01)
                
        except Exception as e:
            logging.error(f"Connection error: {e}")
            logging.info("Falling back to simulation mode...")
            await asyncio.sleep(1)
            # Start simulation when C bot is not available
            await simulate_market_data()

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
    edf_stats = trading_engine.get_edf_stats()
    return {
        "status": "healthy", 
        "connections": len(manager.active_connections),
        "trading_stats": {
            "balance": trading_engine.balance,
            "total_pnl": trading_engine.total_pnl,
            "trade_count": trading_engine.trade_count,
            "active_positions": len(trading_engine.positions)
        },
        "edf_stats": edf_stats
    }

@app.get("/edf-stats")
async def get_edf_statistics():
    """Get detailed EDF performance statistics"""
    stats = trading_engine.get_edf_stats()
    recent_logs = trading_engine.edf_log[-10:] if trading_engine.edf_log else []
    
    return {
        "edf_performance": stats,
        "recent_events": recent_logs,
        "queue_status": {
            "total_tasks": len(trading_engine.task_queue),
            "next_deadline": trading_engine.task_queue[0].deadline_sec if trading_engine.task_queue else None,
            "urgent_tasks": len([t for t in trading_engine.task_queue[:5]])
        }
    }

@app.get("/positions")
async def get_positions():
    positions_data = {}
    for symbol, position in trading_engine.positions.items():
        positions_data[symbol] = {
            "quantity": position.quantity,
            "avg_price": position.avg_price,
            "total_cost": position.total_cost
        }
    return {
        "positions": positions_data,
        "balance": trading_engine.balance,
        "total_pnl": trading_engine.total_pnl
    }

@app.on_event("startup")
async def startup_event():
    logging.info("Starting FastAPI server with EDF trading engine...")
    asyncio.create_task(connect_to_c_bot())

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
