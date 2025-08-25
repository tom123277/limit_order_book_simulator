
import time
import sys
import os
import heapq
import random
from sortedcontainers import SortedDict
import matplotlib.pyplot as plt
from trader_strategies import MarketMaker, MomentumTrader, RandomTrader

# Dynamically add project root to sys.path for portable imports
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)
from order_book.order import LimitOrderBook, Order


NUM_ORDERS = 1000
NUM_TRADERS = 10
TRADER_TYPES = [MarketMaker, MomentumTrader, RandomTrader]

# Helper to generate random orders

def simulate_traders(num_orders, traders):
    orders = []
    for i in range(num_orders):
        trader = random.choice(traders)
        timestamp = time.time() + i * 0.0001
        order = trader.generate_order(i, timestamp)
        orders.append(order)
    return orders

# Benchmark using LimitOrderBook (dict+deque)

def benchmark_limit_order_book_with_traders():
    lob = LimitOrderBook()
    traders = [t(i) for i, t in enumerate(TRADER_TYPES * (NUM_TRADERS // len(TRADER_TYPES)))]
    orders = simulate_traders(NUM_ORDERS, traders)
    spread_history = []
    depth_history = []
    start = time.perf_counter()
    for order in orders:
        lob.add_order(order)
        # Record spread and depth
        if lob.bids and lob.asks:
            best_bid = max(lob.bids.keys())
            best_ask = min(lob.asks.keys())
            spread = best_ask - best_bid
            depth = sum(q.qty for dq in lob.bids.values() for q in dq) + sum(q.qty for dq in lob.asks.values() for q in dq)
            spread_history.append(spread)
            depth_history.append(depth)
    add_time = time.perf_counter() - start
    start = time.perf_counter()
    lob.match()
    match_time = time.perf_counter() - start
    print(f"LimitOrderBook (Traders): Add {add_time:.6f}s, Match {match_time:.6f}s")
    return spread_history, depth_history

# Benchmark using SortedDict
def benchmark_sorted_dict():
    from order_book.order import Side
    book = {Side.BUY: SortedDict(), Side.SELL: SortedDict()}
    traders = [t(i) for i, t in enumerate(TRADER_TYPES * (NUM_TRADERS // len(TRADER_TYPES)))]
    orders = simulate_traders(NUM_ORDERS, traders)
    start = time.perf_counter()
    for order in orders:
        sd = book[order.side]
        if order.price not in sd:
            sd[order.price] = []
        sd[order.price].append(order)
    add_time = time.perf_counter() - start
    print(f"SortedDict: Add {add_time:.6f}s")

# Benchmark using heapq
def benchmark_heapq():
    bids = []
    asks = []
    traders = [t(i) for i, t in enumerate(TRADER_TYPES * (NUM_TRADERS // len(TRADER_TYPES)))]
    orders = simulate_traders(NUM_ORDERS, traders)
    start = time.perf_counter()
    for order in orders:
        if order.side == 'bid':
            heapq.heappush(bids, (-order.price, order.ts, order))
        else:
            heapq.heappush(asks, (order.price, order.ts, order))
    add_time = time.perf_counter() - start
    print(f"heapq: Add {add_time:.6f}s")


if __name__ == "__main__":
    print("Benchmarking Limit Order Book Implementations...")
    spread, depth = benchmark_limit_order_book_with_traders()
    benchmark_sorted_dict()
    benchmark_heapq()
    # Visualization
    plt.figure(figsize=(12,5))
    plt.subplot(1,2,1)
    plt.plot(spread)
    plt.title('Spread Over Time')
    plt.xlabel('Order #')
    plt.ylabel('Spread')
    plt.subplot(1,2,2)
    plt.plot(depth)
    plt.title('Depth Over Time')
    plt.xlabel('Order #')
    plt.ylabel('Depth')
    plt.tight_layout()
    plt.show()
