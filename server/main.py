import asyncio
import threading
import random
import json
import time
import heapq
from enum import Enum
from typing import List, Dict
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import logging

logging.basicConfig(level=logging.INFO, format='%(message)s')
app = FastAPI(title="QuantumCore Elite V4.5 - Zero Loss")

# حل مشكلة الـ 403 Forbidden بشكل نهائي للسماح بالاتصال من أي مصدر
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

RISK_CONFIG = {
    "STOP_LOSS_PCT": 0.003,
    "TAKE_PROFIT_PCT": 0.05,
    "MAX_POSITION_SIZE": 0.02,
    "CIRCUIT_BREAKER": 0.015,
    "EMERGENCY_PRIORITY": 200,
    "GOLD_STABILITY_FACTOR": 0.85
}

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

    def calculate_vd_score(self):
        now = time.time()
        deadline = self.deadline_sec + (self.deadline_usec / 1000000.0)
        time_left = deadline - now
        priority_multiplier = 10.0 if self.type == OrderType.SELL else 1.0
        return (time_left - (self.price * self.quantity * 0.00001)) / (self.priority * priority_multiplier)

    def __lt__(self, other):
        return self.calculate_vd_score() < other.calculate_vd_score()

class TradingPosition:
    def __init__(self, symbol: str):
        self.symbol = symbol
        self.quantity = 0
        self.avg_price = 0.0

    def add(self, qty, prc):
        total_cost = (self.quantity * self.avg_price) + (qty * prc)
        self.quantity += qty
        self.avg_price = total_cost / self.quantity

    def remove(self, qty, prc):
        if qty > self.quantity: qty = self.quantity
        pnl = qty * (prc - self.avg_price)
        self.quantity -= qty
        return pnl

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, ws: WebSocket):
        await ws.accept()
        self.active_connections.append(ws)

    def disconnect(self, ws: WebSocket):
        if ws in self.active_connections: self.active_connections.remove(ws)

    async def broadcast(self, data: dict):
        message = json.dumps(data)
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except:
                continue

manager = ConnectionManager()

class TradingEngine:
    def __init__(self):
        self.task_queue = []
        self.positions: Dict[str, TradingPosition] = {}
        self.balance = 500000.0
        self.initial_balance = 500000.0
        self.total_pnl = 0.0
        self.total_profit = 0.0
        self.total_loss = 0.0
        self.trade_count = 0
        self.lock = threading.Lock()
        self.is_halted = False

    async def execute_next(self, current_prices: dict):
        with self.lock:
            if self.total_pnl < -(self.initial_balance * RISK_CONFIG["CIRCUIT_BREAKER"]):
                self.is_halted = True
                return False

            if not self.task_queue: return False
            task = heapq.heappop(self.task_queue)
            symbol = task.symbol
            pos = self.positions.get(symbol, TradingPosition(symbol))
            self.positions[symbol] = pos
            market_price = current_prices.get(symbol, task.price)

            if task.type == OrderType.SELL and pos.quantity >= task.quantity:
                pnl = pos.remove(task.quantity, market_price)
                self.balance += (market_price * task.quantity)
                self.total_pnl += pnl
                if pnl > 0:
                    self.total_profit += pnl
                else:
                    self.total_loss += abs(pnl)
                self.trade_count += 1
                asyncio.create_task(manager.broadcast({
                    "type": "order", "order_type": "SELL", "symbol": symbol,
                    "price": round(market_price, 2), "quantity": task.quantity, "pnl": round(pnl, 2)
                }))
                return True
            elif task.type == OrderType.BUY and not self.is_halted:
                max_allowed = self.balance * RISK_CONFIG["MAX_POSITION_SIZE"]
                cost = market_price * task.quantity
                if cost > max_allowed:
                    task.quantity = int(max_allowed / market_price)
                    cost = market_price * task.quantity
                if task.quantity > 0 and self.balance >= cost:
                    pos.add(task.quantity, market_price)
                    self.balance -= cost
                    self.trade_count += 1
                    asyncio.create_task(manager.broadcast({
                        "type": "order", "order_type": "BUY", "symbol": symbol,
                        "price": round(market_price, 2), "quantity": task.quantity, "pnl": None
                    }))
                    return True
            return False

    def get_stats(self, symbol, price, all_prices):
        with self.lock:
            # إصلاح الـ NameError: تعريف win_rate وحسابها
            total_resolved = self.total_profit + self.total_loss
            current_win_rate = 0.0
            if total_resolved > 0:
                current_win_rate = round((self.total_profit / total_resolved) * 100, 1)

            # إصلاح الـ NameError: تعريف portfolio_data
            portfolio_data = {
                s: round(p.quantity * all_prices.get(s, p.avg_price), 2)
                for s, p in self.positions.items() if p.quantity > 0
            }

            return {
                "type": "update",
                "symbol": symbol,
                "price": round(price, 2),
                "balance": round(self.balance, 2),
                "pnl": round(self.total_pnl, 2),
                "total_profit": round(self.total_profit, 2),
                "trade_count": self.trade_count,
                "win_rate": current_win_rate,
                "queue_size": len(self.task_queue),
                "portfolio": portfolio_data,
                "all_prices": {s: round(p, 2) for s, p in all_prices.items()}
            }

trading_engine = TradingEngine()

# مسار Health Check لتجنب خطأ 404 في السجلات
@app.get("/health")
async def health_check():
    return {"status": "online"}

async def market_simulator():
    asset_configs = {
        "GOLD_OUNCE": {"price": 2350.0, "vol": 0.003},
        "GOLD_KILO": {"price": 75000.0, "vol": 0.002},
        "ROLEX_SUB": {"price": 15000.0, "vol": 0.015},
        "MACBOOK_M3": {"price": 2500.0, "vol": 0.03},
        "NVIDIA_RTX4090": {"price": 1600.0, "vol": 0.04}
    }
    current_prices = {s: conf["price"] for s, conf in asset_configs.items()}
    while True:
        symbol = random.choice(
            [s for s in asset_configs.keys() if "GOLD" in s]) if random.random() < 0.85 else random.choice(
            list(asset_configs.keys()))
        config = asset_configs[symbol]
        current_prices[symbol] *= (1 + random.uniform(-config["vol"], config["vol"]) * 0.05)

        pos = trading_engine.positions.get(symbol)
        if pos and pos.quantity > 0:
            if current_prices[symbol] <= pos.avg_price * (1 - 0.003) or current_prices[symbol] >= pos.avg_price * (1 + 0.05):
                heapq.heappush(trading_engine.task_queue,
                               TradingTask(id=random.randint(1, 999), type=OrderType.SELL, symbol=symbol,
                                           price=current_prices[symbol], quantity=pos.quantity,
                                           deadline_sec=int(time.time()), deadline_usec=0, created_sec=int(time.time()),
                                           created_usec=0, priority=200))

        if not trading_engine.is_halted and random.random() < 0.25:
            heapq.heappush(trading_engine.task_queue,
                           TradingTask(id=random.randint(1, 999), type=OrderType.BUY, symbol=symbol,
                                       price=current_prices[symbol], quantity=random.randint(1, 2),
                                       deadline_sec=int(time.time()) + 5, deadline_usec=0, created_sec=int(time.time()),
                                       created_usec=0, priority=1))

        while trading_engine.task_queue:
            if not await trading_engine.execute_next(current_prices): break

        await manager.broadcast(trading_engine.get_stats(symbol, current_prices[symbol], current_prices))
        await asyncio.sleep(0.1)

@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    await manager.connect(ws)
    try:
        while True: await ws.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(ws)
    except:
        manager.disconnect(ws)

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(market_simulator())

if __name__ == "__main__":
    import uvicorn
    # التشغيل على 0.0.0.0 ليقبل الاتصال من خارج الحاوية
    uvicorn.run(app, host="0.0.0.0", port=8000)