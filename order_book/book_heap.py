# heapq-based order book implementation
import heapq
from collections import deque
from typing import Dict, List, Tuple
from .order import Order, Trade, Side, OrderType

class HeapOrderBook:
    def __init__(self):
        self.bid_heap: List[float] = []  # max-heap (store -price)
        self.ask_heap: List[float] = []  # min-heap
        self.bids: Dict[float, deque] = {}
        self.asks: Dict[float, deque] = {}
        self.order_map: Dict[int, Order] = {}

    def add_order(self, order: Order):
        if order.type == OrderType.LIMIT:
            if order.price is None:
                raise ValueError("Limit order must have a price.")
            if order.side == Side.BUY:
                if order.price not in self.bids:
                    self.bids[order.price] = deque()
                    heapq.heappush(self.bid_heap, -order.price)
                self.bids[order.price].append(order)
            else:
                if order.price not in self.asks:
                    self.asks[order.price] = deque()
                    heapq.heappush(self.ask_heap, order.price)
                self.asks[order.price].append(order)
            self.order_map[order.id] = order
        elif order.type == OrderType.MARKET:
            pass  # Matching logic elsewhere

    def cancel_order(self, order_id: int) -> bool:
        order = self.order_map.get(order_id)
        if not order or order.type != OrderType.LIMIT or order.price is None:
            return False
        book = self.bids if order.side == Side.BUY else self.asks
        queue = book.get(order.price)
        if queue:
            for idx, o in enumerate(queue):
                if o.id == order_id:
                    del queue[idx]
                    del self.order_map[order_id]
                    # Lazy deletion: don't remove price from heap yet
                    return True
        return False

    def best_bid(self):
        while self.bid_heap:
            price = -self.bid_heap[0]
            if price in self.bids and self.bids[price]:
                return price, sum(o.qty for o in self.bids[price])
            heapq.heappop(self.bid_heap)  # lazy cleanup
        return None

    def best_ask(self):
        while self.ask_heap:
            price = self.ask_heap[0]
            if price in self.asks and self.asks[price]:
                return price, sum(o.qty for o in self.asks[price])
            heapq.heappop(self.ask_heap)
        return None

    def match(self) -> List[Trade]:
        trades: List[Trade] = []
        while True:
            best_bid = self.best_bid()
            best_ask = self.best_ask()
            if not best_bid or not best_ask or best_bid[0] < best_ask[0]:
                break
            bid_queue = self.bids[best_bid[0]]
            ask_queue = self.asks[best_ask[0]]
            bid_order = bid_queue[0]
            ask_order = ask_queue[0]
            trade_qty = min(bid_order.qty, ask_order.qty)
            trade = Trade(
                ts=max(bid_order.ts, ask_order.ts),
                price=best_ask[0],
                qty=trade_qty,
                maker_id=ask_order.id,
                taker_id=bid_order.id
            )
            trades.append(trade)
            bid_order.qty -= trade_qty
            ask_order.qty -= trade_qty
            if bid_order.qty == 0:
                bid_queue.popleft()
                del self.order_map[bid_order.id]
            if ask_order.qty == 0:
                ask_queue.popleft()
                del self.order_map[ask_order.id]
            if not bid_queue:
                del self.bids[best_bid[0]]
            if not ask_queue:
                del self.asks[best_ask[0]]
        return trades
