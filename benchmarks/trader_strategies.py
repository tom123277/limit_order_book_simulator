import random
import time
import sys
import os
# Dynamically add project root to sys.path for portable imports
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)
from order_book.order import Order, Side, OrderType

class Trader:
    def __init__(self, trader_id):
        self.trader_id = trader_id

    def generate_order(self, order_id, timestamp):
        raise NotImplementedError

class MarketMaker(Trader):
    def generate_order(self, order_id, timestamp):
        # Places bid and ask near mid price
        mid = 100.0
        spread = 0.1
        side = Side.BUY if random.random() < 0.5 else Side.SELL
        price = mid - spread if side == Side.BUY else mid + spread
        qty = random.randint(1, 5)
        return Order(order_id, timestamp, side, OrderType.LIMIT, price, qty)

class MomentumTrader(Trader):
    def generate_order(self, order_id, timestamp):
        # Buys if price is rising, sells if falling (simplified)
        side = Side.BUY if random.random() < 0.7 else Side.SELL
        price = 100.0 + random.uniform(-0.5, 0.5)
        qty = random.randint(1, 3)
        return Order(order_id, timestamp, side, OrderType.LIMIT, price, qty)

class RandomTrader(Trader):
    def generate_order(self, order_id, timestamp):
        side = Side.BUY if random.random() < 0.5 else Side.SELL
        price = round(random.uniform(99, 101), 2)
        qty = random.randint(1, 10)
        return Order(order_id, timestamp, side, OrderType.LIMIT, price, qty)
