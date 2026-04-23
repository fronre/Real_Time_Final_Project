#!/usr/bin/env python3
"""
Real-Time Trading Engine with EDF Scheduling
Hard Real-Time System for Digital Asset Trading
"""

import asyncio
import heapq
import time
import logging
import json
import threading
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
import random
import numpy as np
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s.%(msecs)03d [%(levelname)s] %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(__name__)

class OrderType(Enum):
    BUY = "BUY"
    SELL = "SELL"

class TradingStrategy(Enum):
    THRESHOLD = "Threshold"
    MOVING_AVERAGE = "Moving Average"
    MOMENTUM = "Momentum"

@dataclass
class TradingTask:
    """Real-Time Trading Task with EDF Scheduling"""
    id: int
    order_type: OrderType
    symbol: str
    price: float
    quantity: int
    deadline: float  # microseconds
    created_time: float
    execution_time: float = 0.0
    priority: int = 0
    strategy: TradingStrategy = TradingStrategy.THRESHOLD
    confidence: float = 0.0
    
    def __lt__(self, other):
        """EDF: Compare by deadline (earliest deadline first)"""
        return self.deadline < other.deadline

@dataclass
class MarketData:
    """Real-Time Market Data with Microsecond Precision"""
    symbol: str
    price: float
    volume: int
    timestamp: float  # microseconds
    volatility: float
    trend: float
    bid: float = 0.0
    ask: float = 0.0
    spread: float = 0.0

@dataclass
class Position:
    """Trading Position with Risk Management"""
    symbol: str
    quantity: int
    entry_price: float
    current_price: float
    unrealized_pnl: float = 0.0
    realized_pnl: float = 0.0
    stop_loss: float = 0.0
    take_profit: float = 0.0
    entry_time: float = 0.0
    
    def update_pnl(self, current_price: float):
        """Update P&L based on current price"""
        self.current_price = current_price
        if self.quantity > 0:  # Long position
            self.unrealized_pnl = (current_price - self.entry_price) * self.quantity
        else:  # Short position
            self.unrealized_pnl = (self.entry_price - current_price) * abs(self.quantity)

class RiskManager:
    """Risk Management System"""
    
    def __init__(self, max_position_size: int = 1000, max_loss_percent: float = 0.02):
        self.max_position_size = max_position_size
        self.max_loss_percent = max_loss_percent
        self.daily_loss_limit = 10000.0
        self.daily_pnl = 0.0
        
    def check_position_size(self, quantity: int) -> bool:
        """Check if position size is within limits"""
        return abs(quantity) <= self.max_position_size
    
    def calculate_stop_loss(self, entry_price: float, volatility: float) -> float:
        """Calculate stop loss based on volatility"""
        return entry_price * (1 - 2 * volatility)  # 2x volatility stop loss
    
    def calculate_take_profit(self, entry_price: float, volatility: float) -> float:
        """Calculate take profit based on volatility"""
        return entry_price * (1 + 3 * volatility)  # 3x volatility take profit
    
    def check_daily_loss(self) -> bool:
        """Check if daily loss limit is reached"""
        return self.daily_pnl >= -self.daily_loss_limit

class TradingStrategies:
    """Advanced Trading Strategies"""
    
    @staticmethod
    def threshold_strategy(market_data: MarketData, history: List[MarketData]) -> Tuple[bool, float]:
        """Threshold-based trading strategy"""
        if len(history) < 10:
            return False, 0.0
        
        avg_price = sum(data.price for data in history[-10:]) / 10
        current_price = market_data.price
        
        # Buy if price is 2% below average
        if current_price < avg_price * 0.98:
            return True, 0.7
        # Sell if price is 2% above average
        elif current_price > avg_price * 1.02:
            return True, 0.7
        
        return False, 0.0
    
    @staticmethod
    def moving_average_strategy(market_data: MarketData, history: List[MarketData]) -> Tuple[bool, float]:
        """Moving Average crossover strategy"""
        if len(history) < 20:
            return False, 0.0
        
        prices = [data.price for data in history[-20:]]
        ma_short = sum(prices[-5:]) / 5  # 5-period MA
        ma_long = sum(prices[-20:]) / 20  # 20-period MA
        current_price = market_data.price
        
        # Buy signal: short MA crosses above long MA
        if ma_short > ma_long and current_price > ma_short:
            return True, 0.8
        # Sell signal: short MA crosses below long MA
        elif ma_short < ma_long and current_price < ma_short:
            return True, 0.8
        
        return False, 0.0
    
    @staticmethod
    def momentum_strategy(market_data: MarketData, history: List[MarketData]) -> Tuple[bool, float]:
        """Momentum-based trading strategy"""
        if len(history) < 15:
            return False, 0.0
        
        # Calculate momentum (price change over last 15 periods)
        momentum = (market_data.price - history[-15].price) / history[-15].price
        
        # Strong momentum (>1%)
        if abs(momentum) > 0.01:
            confidence = min(abs(momentum) * 50, 0.9)  # Cap at 90%
            return True, confidence
        
        return False, 0.0

class RealTimeTradingEngine:
    """Hard Real-Time Trading Engine with EDF Scheduling"""
    
    def __init__(self):
        self.task_queue: List[TradingTask] = []
        self.positions: Dict[str, Position] = {}
        self.market_history: Dict[str, List[MarketData]] = {}
        self.balance = 100000.0  # Starting balance
        self.total_pnl = 0.0
        self.trade_count = 0
        self.task_id_counter = 0
        self.risk_manager = RiskManager()
        self.strategies = TradingStrategies()
        self.fee_rate = 0.001  # 0.1% trading fee
        self.slippage_model = 0.0001  # 0.01% slippage
        
        # Real-time performance metrics
        self.deadline_misses = 0
        self.total_tasks = 0
        self.avg_execution_time = 0.0
        
        logger.info("🚀 Real-Time Trading Engine initialized")
        logger.info(f"💰 Starting balance: ${self.balance:,.2f}")
    
    def get_microsecond_timestamp(self) -> float:
        """Get current timestamp in microseconds"""
        return time.time() * 1_000_000
    
    def create_trading_task(self, order_type: OrderType, symbol: str, 
                          price: float, quantity: int, strategy: TradingStrategy,
                          confidence: float, deadline_offset_ms: float = 100.0) -> TradingTask:
        """Create a new trading task with deadline"""
        current_time = self.get_microsecond_timestamp()
        deadline = current_time + (deadline_offset_ms * 1000)  # Convert to microseconds
        
        task = TradingTask(
            id=self.task_id_counter,
            order_type=order_type,
            symbol=symbol,
            price=price,
            quantity=quantity,
            deadline=deadline,
            created_time=current_time,
            strategy=strategy,
            confidence=confidence
        )
        
        self.task_id_counter += 1
        return task
    
    def add_task(self, task: TradingTask):
        """Add task to EDF queue"""
        heapq.heappush(self.task_queue, task)
        logger.info(f"📋 Task added: {task.order_type.value} {task.quantity} {task.symbol} @ ${task.price:.6f}")
        logger.info(f"⏰ Deadline: {task.deadline:.0f}μs (in {(task.deadline - task.created_time)/1000:.1f}ms)")
    
    def get_next_task(self) -> Optional[TradingTask]:
        """Get next task using EDF (earliest deadline first)"""
        if not self.task_queue:
            return None
        
        current_time = self.get_microsecond_timestamp()
        task = heapq.heappop(self.task_queue)
        
        # Check if deadline is missed
        if current_time > task.deadline:
            self.deadline_misses += 1
            logger.warning(f"⚠️ DEADLINE MISSED: Task {task.id} by {(current_time - task.deadline)/1000:.1f}ms")
            return None
        
        return task
    
    def execute_task(self, task: TradingTask, current_price: float) -> bool:
        """Execute trading task with real market conditions"""
        start_time = self.get_microsecond_timestamp()
        
        try:
            # Apply slippage
            execution_price = task.price * (1 + self.slippage_model if task.order_type == OrderType.BUY else -self.slippage_model)
            
            # Calculate fees
            fee = execution_price * task.quantity * self.fee_rate
            
            # Check risk management
            if not self.risk_manager.check_position_size(task.quantity):
                logger.warning(f"❌ Position size too large: {task.quantity}")
                return False
            
            if not self.risk_manager.check_daily_loss():
                logger.warning(f"❌ Daily loss limit reached")
                return False
            
            # Execute trade
            if task.order_type == OrderType.BUY:
                cost = execution_price * task.quantity + fee
                if cost > self.balance:
                    logger.warning(f"❌ Insufficient balance: need ${cost:.2f}, have ${self.balance:.2f}")
                    return False
                
                # Create or update position
                if task.symbol in self.positions:
                    pos = self.positions[task.symbol]
                    # Average down/up
                    total_cost = pos.entry_price * pos.quantity + cost
                    pos.quantity += task.quantity
                    pos.entry_price = total_cost / pos.quantity
                else:
                    self.positions[task.symbol] = Position(
                        symbol=task.symbol,
                        quantity=task.quantity,
                        entry_price=execution_price,
                        current_price=current_price,
                        stop_loss=self.risk_manager.calculate_stop_loss(execution_price, 0.1),
                        take_profit=self.risk_manager.calculate_take_profit(execution_price, 0.1),
                        entry_time=start_time
                    )
                
                self.balance -= cost
                
            else:  # SELL
                if task.symbol not in self.positions or self.positions[task.symbol].quantity < task.quantity:
                    logger.warning(f"❌ No position to sell: {task.symbol}")
                    return False
                
                pos = self.positions[task.symbol]
                proceeds = execution_price * task.quantity - fee
                
                # Calculate realized P&L
                realized_pnl = (execution_price - pos.entry_price) * task.quantity
                pos.realized_pnl += realized_pnl
                pos.quantity -= task.quantity
                
                if pos.quantity == 0:
                    del self.positions[task.symbol]
                
                self.balance += proceeds
                self.total_pnl += realized_pnl
                self.risk_manager.daily_pnl += realized_pnl
            
            # Log the trade
            execution_time = (self.get_microsecond_timestamp() - start_time) / 1000
            logger.info(f"✅ EXECUTED: {task.order_type.value} {task.quantity} {task.symbol} @ ${execution_price:.6f}")
            logger.info(f"💰 Fee: ${fee:.4f} | Execution time: {execution_time:.2f}ms")
            logger.info(f"📊 Balance: ${self.balance:.2f} | P&L: ${self.total_pnl:.2f}")
            
            self.trade_count += 1
            self.total_tasks += 1
            self.avg_execution_time = (self.avg_execution_time * (self.trade_count - 1) + execution_time) / self.trade_count
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Task execution failed: {e}")
            return False
    
    def analyze_market_and_create_tasks(self, market_data: MarketData):
        """Analyze market data and create trading tasks"""
        symbol = market_data.symbol
        
        # Store market data in history
        if symbol not in self.market_history:
            self.market_history[symbol] = []
        self.market_history[symbol].append(market_data)
        
        # Keep only last 100 data points
        if len(self.market_history[symbol]) > 100:
            self.market_history[symbol] = self.market_history[symbol][-100:]
        
        # Apply trading strategies
        history = self.market_history[symbol]
        
        # Test all strategies
        strategies = [
            (TradingStrategy.THRESHOLD, self.strategies.threshold_strategy),
            (TradingStrategy.MOVING_AVERAGE, self.strategies.moving_average_strategy),
            (TradingStrategy.MOMENTUM, self.strategies.momentum_strategy)
        ]
        
        for strategy_enum, strategy_func in strategies:
            should_trade, confidence = strategy_func(market_data, history)
            
            if should_trade and confidence > 0.5:  # Minimum confidence threshold
                # Determine order type based on market conditions
                order_type = OrderType.BUY if market_data.trend > 0 else OrderType.SELL
                
                # Calculate position size based on confidence
                base_quantity = 10
                quantity = int(base_quantity * confidence)
                
                # Create task with deadline based on strategy confidence
                deadline_offset = 200.0 / confidence  # Higher confidence = tighter deadline
                
                task = self.create_trading_task(
                    order_type=order_type,
                    symbol=symbol,
                    price=market_data.price,
                    quantity=quantity,
                    strategy=strategy_enum,
                    confidence=confidence,
                    deadline_offset_ms=deadline_offset
                )
                
                self.add_task(task)
    
    def check_risk_management(self):
        """Check all positions for stop loss and take profit"""
        for symbol, position in list(self.positions.items()):
            current_price = self.market_history.get(symbol, [MarketData(symbol, position.entry_price, 0, 0, 0, 0)])[-1].price
            
            position.update_pnl(current_price)
            
            # Check stop loss
            if current_price <= position.stop_loss:
                logger.warning(f"🛑 STOP LOSS triggered for {symbol}")
                task = self.create_trading_task(
                    OrderType.SELL, symbol, current_price, position.quantity,
                    TradingStrategy.THRESHOLD, 1.0, 50.0  # Emergency execution
                )
                self.add_task(task)
            
            # Check take profit
            elif current_price >= position.take_profit:
                logger.info(f"🎯 TAKE PROFIT triggered for {symbol}")
                task = self.create_trading_task(
                    OrderType.SELL, symbol, current_price, position.quantity,
                    TradingStrategy.THRESHOLD, 1.0, 50.0  # Emergency execution
                )
                self.add_task(task)
    
    def process_tasks(self):
        """Process all tasks in EDF order"""
        while self.task_queue:
            task = self.get_next_task()
            if task is None:
                break
            
            # Get current market price
            current_price = self.market_history.get(task.symbol, [MarketData(task.symbol, task.price, 0, 0, 0, 0)])[-1].price
            
            # Execute the task
            self.execute_task(task, current_price)
    
    def get_system_status(self) -> Dict:
        """Get comprehensive system status"""
        return {
            "balance": self.balance,
            "total_pnl": self.total_pnl,
            "trade_count": self.trade_count,
            "active_positions": len(self.positions),
            "pending_tasks": len(self.task_queue),
            "deadline_misses": self.deadline_misses,
            "deadline_miss_rate": self.deadline_misses / max(self.total_tasks, 1),
            "avg_execution_time_ms": self.avg_execution_time,
            "positions": {
                symbol: {
                    "quantity": pos.quantity,
                    "entry_price": pos.entry_price,
                    "current_price": pos.current_price,
                    "unrealized_pnl": pos.unrealized_pnl,
                    "realized_pnl": pos.realized_pnl
                }
                for symbol, pos in self.positions.items()
            }
        }

# Initialize the trading engine
trading_engine = RealTimeTradingEngine()

class RealTimeTradingAPI(BaseHTTPRequestHandler):
    """Real-Time Trading API with Microsecond Precision"""
    
    def do_GET(self):
        parsed_path = urlparse(self.path)
        
        if parsed_path.path == '/api/market-data':
            self.send_real_market_data()
        elif parsed_path.path == '/api/status':
            self.send_system_status()
        elif parsed_path.path == '/api/positions':
            self.send_positions()
        elif parsed_path.path == '/health':
            self.send_health()
        else:
            self.send_404()
    
    def send_real_market_data(self):
        """Generate realistic market data with microsecond precision"""
        current_time = trading_engine.get_microsecond_timestamp()
        
        # Simulate 10 digital assets with realistic correlations
        assets = [
            {"symbol": "BTC", "base_price": 45000, "volatility": 0.08, "trend_strength": 0.3},
            {"symbol": "ETH", "base_price": 3000, "volatility": 0.10, "trend_strength": 0.4},
            {"symbol": "USDT", "base_price": 1.0, "volatility": 0.01, "trend_strength": 0.1},
            {"symbol": "PUBG_UC", "base_price": 0.01, "volatility": 0.15, "trend_strength": 0.5},
            {"symbol": "COD_POINTS", "base_price": 0.02, "volatility": 0.12, "trend_strength": 0.4},
            {"symbol": "NETFLIX", "base_price": 15.0, "volatility": 0.05, "trend_strength": 0.2},
            {"symbol": "SPOTIFY", "base_price": 10.0, "volatility": 0.04, "trend_strength": 0.2},
            {"symbol": "VPN_PREMIUM", "base_price": 5.0, "volatility": 0.03, "trend_strength": 0.1},
            {"symbol": "DOMAIN_COM", "base_price": 25.0, "volatility": 0.06, "trend_strength": 0.3},
            {"symbol": "NFT_ART", "base_price": 100.0, "volatility": 0.20, "trend_strength": 0.6}
        ]
        
        # Select current asset (rotate every 100ms)
        asset_index = int(current_time / 100000) % len(assets)
        asset = assets[asset_index]
        
        # Generate realistic price movement
        time_factor = current_time / 1000000  # Convert to seconds
        price_change = (
            np.sin(time_factor * 0.1) * asset["volatility"] * asset["base_price"] * 0.5 +
            np.sin(time_factor * 0.3) * asset["volatility"] * asset["base_price"] * 0.3 +
            np.random.normal(0, asset["volatility"] * asset["base_price"] * 0.1)
        )
        
        current_price = asset["base_price"] + price_change
        volume = int(np.random.normal(1000, 200) * (1 + asset["volatility"]))
        trend = np.sin(time_factor * asset["trend_strength"]) * 0.5
        
        # Create bid-ask spread
        spread = current_price * 0.0001  # 0.01% spread
        bid = current_price - spread / 2
        ask = current_price + spread / 2
        
        market_data = MarketData(
            symbol=asset["symbol"],
            price=current_price,
            volume=volume,
            timestamp=current_time,
            volatility=asset["volatility"],
            trend=trend,
            bid=bid,
            ask=ask,
            spread=spread
        )
        
        # Analyze market and create trading tasks
        trading_engine.analyze_market_and_create_tasks(market_data)
        
        # Check risk management
        trading_engine.check_risk_management()
        
        # Process pending tasks (EDF execution)
        trading_engine.process_tasks()
        
        # Prepare response
        response_data = {
            "type": "market_data",
            "timestamp": current_time,
            "data": {
                "symbol": market_data.symbol,
                "price": round(market_data.price, 6),
                "bid": round(market_data.bid, 6),
                "ask": round(market_data.ask, 6),
                "spread": round(market_data.spread, 6),
                "volume": market_data.volume,
                "timestamp_sec": int(current_time / 1_000_000),
                "timestamp_usec": int(current_time % 1_000_000),
                "volatility": round(market_data.volatility, 4),
                "trend": round(market_data.trend, 4)
            },
            "trading_stats": trading_engine.get_system_status(),
            "system_performance": {
                "deadline_miss_rate": trading_engine.deadline_misses / max(trading_engine.total_tasks, 1),
                "avg_execution_time_ms": trading_engine.avg_execution_time,
                "pending_tasks": len(trading_engine.task_queue)
            }
        }
        
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(response_data, indent=2).encode())
        
        logger.info(f"📊 {market_data.symbol}: ${market_data.price:.6f} | Tasks: {len(trading_engine.task_queue)}")
    
    def send_system_status(self):
        status = trading_engine.get_system_status()
        
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(status, indent=2).encode())
    
    def send_positions(self):
        positions = trading_engine.get_system_status()["positions"]
        
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(positions, indent=2).encode())
    
    def send_health(self):
        health = {
            "status": "healthy",
            "timestamp": trading_engine.get_microsecond_timestamp(),
            "service": "realtime-trading-engine",
            "system_type": "Soft Real-Time",
            "scheduling_algorithm": "EDF (Earliest Deadline First)",
            "precision": "microseconds",
            "deadline_miss_rate": trading_engine.deadline_misses / max(trading_engine.total_tasks, 1)
        }
        
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(health, indent=2).encode())
    
    def send_404(self):
        self.send_response(404)
        self.end_headers()
        self.wfile.write(b'Not Found')
    
    def log_message(self, format, *args):
        # Disable default logging
        pass

def run_realtime_server():
    """Run the real-time trading server"""
    server = HTTPServer(('localhost', 8001), RealTimeTradingAPI)
    
    logger.info("🚀 REAL-TIME TRADING ENGINE STARTED")
    logger.info("=" * 60)
    logger.info("📊 System Configuration:")
    logger.info("   • Type: Soft Real-Time System")
    logger.info("   • Scheduling: EDF (Earliest Deadline First)")
    logger.info("   • Precision: Microseconds (μs)")
    logger.info("   • Assets: 10 Digital Assets")
    logger.info("   • Strategies: Threshold, Moving Average, Momentum")
    logger.info("   • Risk Management: Stop Loss, Take Profit, Position Limits")
    logger.info("=" * 60)
    logger.info("🌐 API Endpoints:")
    logger.info("   • GET /api/market-data (Real-time market data & trading)")
    logger.info("   • GET /api/status (System status & P&L)")
    logger.info("   • GET /api/positions (Active positions)")
    logger.info("   • GET /health (Health check)")
    logger.info("=" * 60)
    logger.info("🎯 Ready for trading! Open frontend to see live trading!")
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        logger.info("\n👋 Real-Time Trading Engine stopped by user")
        logger.info(f"📊 Final Stats:")
        logger.info(f"   • Total Trades: {trading_engine.trade_count}")
        logger.info(f"   • Total P&L: ${trading_engine.total_pnl:.2f}")
        logger.info(f"   • Final Balance: ${trading_engine.balance:.2f}")
        logger.info(f"   • Deadline Miss Rate: {trading_engine.deadline_misses / max(trading_engine.total_tasks, 1):.2%}")
        server.shutdown()

if __name__ == "__main__":
    run_realtime_server()
