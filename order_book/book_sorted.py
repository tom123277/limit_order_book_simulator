# sortedcontainers-based order book implementation
from sortedcontainers import SortedDict
from collections import deque
from typing import List
from .order import Order, Trade, Side, OrderType

class SortedOrderBook:
    def __init__(self):
        self.bids = SortedDict()
        self.asks = SortedDict()
        self.order_map = {}

    def add_order(self, order: Order):
        if order.type == OrderType.LIMIT:
            if order.price is None:
                raise ValueError("Limit order must have a price.")
            book = self.bids if order.side == Side.BUY else self.asks
            if order.price not in book:
                book[order.price] = deque()
            book[order.price].append(order)
            self.order_map[order.id] = order
        elif order.type == OrderType.MARKET:
            pass

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
                    if not queue:
                        del book[order.price]
                    return True
        return False

    def best_bid(self):
        if not self.bids:
            return None
        price = self.bids.peekitem(-1)[0]
        qty = sum(o.qty for o in self.bids[price])
        return (price, qty)

    def best_ask(self):
        if not self.asks:
            return None
        price = self.asks.peekitem(0)[0]
        qty = sum(o.qty for o in self.asks[price])
        return (price, qty)

    def match(self) -> List[Trade]:
        trades: List[Trade] = []
        while self.bids and self.asks:
            best_bid = self.best_bid()
            best_ask = self.best_ask()
            if not best_bid or not best_ask or best_bid[0] < best_ask[0]:
                break
            bid_queue = self.bids[best_bid[0]]
            ask_queue = self.asks[best_ask[0]]
            bid_order = bid_queue[0]
            ask_order = ask_queue[0]
            trade_qty = min(bid_order.qty, ask_order.qty)
            price = best_ask[0]
            if not isinstance(price, float):
                break
            trade = Trade(
                ts=max(bid_order.ts, ask_order.ts),
                price=price,
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
