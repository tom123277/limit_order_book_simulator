
from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional

class Side(Enum):
    BUY = auto()
    SELL = auto()

class OrderType(Enum):
    LIMIT = auto()
    MARKET = auto()

@dataclass
class Order:
    id: int
    ts: float
    side: Side
    type: OrderType
    price: Optional[float]
    qty: int
    owner: Optional[str] = None
    flags: Optional[str] = None

@dataclass
class Trade:
    ts: float
    price: float
    qty: int
    maker_id: int
    taker_id: int

from collections import deque
from typing import Dict, List

class LimitOrderBook:
    def __init__(self):
        self.bids: Dict[float, deque] = {}
        self.asks: Dict[float, deque] = {}
        self.order_map: Dict[int, Order] = {}


    def add_order(self, order: Order):
        # Only add LIMIT orders to the book
        if order.type == OrderType.LIMIT:
            if order.price is None:
                raise ValueError("Limit order must have a price.")
            book = self.bids if order.side == Side.BUY else self.asks
            if order.price not in book:
                book[order.price] = deque()
            book[order.price].append(order)
            self.order_map[order.id] = order
        elif order.type == OrderType.MARKET:
            # Market orders should be matched immediately, not stored
            pass  # Matching logic should be handled elsewhere

    def cancel_order(self, order_id: int) -> bool:
        order = self.order_map.get(order_id)
        if not order:
            return False
        if order.type != OrderType.LIMIT or order.price is None:
            return False  # Only limit orders with price can be canceled from book
        book = self.bids if order.side == Side.BUY else self.asks
        queue = book.get(order.price)
        if queue:
            for idx, o in enumerate(queue):
                if o.id == order_id:
                    del queue[idx]
                    del self.order_map[order_id]
                    return True
        return False


    def match(self) -> List[Trade]:
        trades: List[Trade] = []
        if not self.bids or not self.asks:
            return trades
        best_bid = max(self.bids.keys()) if self.bids else None
        best_ask = min(self.asks.keys()) if self.asks else None
        while best_bid is not None and best_ask is not None and best_bid >= best_ask:
            bid_queue = self.bids[best_bid]
            ask_queue = self.asks[best_ask]
            bid_order = bid_queue[0]
            ask_order = ask_queue[0]
            trade_qty = min(bid_order.qty, ask_order.qty)
            trade = Trade(
                ts=max(bid_order.ts, ask_order.ts),
                price=best_ask,
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
                del self.bids[best_bid]
            if not ask_queue:
                del self.asks[best_ask]
            best_bid = max(self.bids.keys()) if self.bids else None
            best_ask = min(self.asks.keys()) if self.asks else None
        return trades

    def get_orders_at_price(self, side: Side, price: float) -> List[Order]:
        if side == Side.BUY:
            return list(self.bids.get(price, []))
        else:
            return list(self.asks.get(price, []))

    def depth(self, k: int = 5) -> dict:
        """
        Returns L2 depth snapshot: top-k price levels for bids and asks.
        Output: {'bids': [(price, qty)], 'asks': [(price, qty)]}
        """
        bid_levels = sorted(self.bids.keys(), reverse=True)[:k]
        ask_levels = sorted(self.asks.keys())[:k]
        bids = [(p, sum(o.qty for o in self.bids[p])) for p in bid_levels]
        asks = [(p, sum(o.qty for o in self.asks[p])) for p in ask_levels]
        return {'bids': bids, 'asks': asks}
