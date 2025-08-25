
from .order import Order, Trade, Side, OrderType
from .book_base import OrderBook


class Matcher:
    def __init__(self, book: OrderBook):
        self.book = book

    def submit(self, order: Order) -> list:
        trades = []
        if order.type == OrderType.LIMIT:
            self.book.add_order(order)
            trades = self.book.match()
        elif order.type == OrderType.MARKET:
            trades = self._match_market(order)
        return trades

    def _match_market(self, order: Order) -> list:
        trades = []
        qty_remaining = order.qty
        # Use depth() to get sorted price levels and quantities
        if order.side == Side.BUY:
            # Match against asks from lowest price up
            depth = self.book.depth(k=1000000)  # large k to get all levels
            for price, level_qty in depth['asks']:
                while level_qty > 0 and qty_remaining > 0:
                    # Find the first order at this price
                    ask_orders = self._get_orders_at_price(orderbook=self.book, side=Side.SELL, price=price)
                    if not ask_orders:
                        break
                    ask_order = ask_orders[0]
                    trade_qty = min(qty_remaining, ask_order.qty)
                    trade = Trade(
                        ts=max(order.ts, ask_order.ts),
                        price=price,
                        qty=trade_qty,
                        maker_id=ask_order.id,
                        taker_id=order.id
                    )
                    trades.append(trade)
                    ask_order.qty -= trade_qty
                    qty_remaining -= trade_qty
                    if ask_order.qty == 0:
                        self.book.cancel_order(ask_order.id)
                    level_qty -= trade_qty
                if qty_remaining == 0:
                    break
        else:
            # Match against bids from highest price down
            depth = self.book.depth(k=1000000)
            for price, level_qty in depth['bids']:
                while level_qty > 0 and qty_remaining > 0:
                    bid_orders = self._get_orders_at_price(orderbook=self.book, side=Side.BUY, price=price)
                    if not bid_orders:
                        break
                    bid_order = bid_orders[0]
                    trade_qty = min(qty_remaining, bid_order.qty)
                    trade = Trade(
                        ts=max(order.ts, bid_order.ts),
                        price=price,
                        qty=trade_qty,
                        maker_id=bid_order.id,
                        taker_id=order.id
                    )
                    trades.append(trade)
                    bid_order.qty -= trade_qty
                    qty_remaining -= trade_qty
                    if bid_order.qty == 0:
                        self.book.cancel_order(bid_order.id)
                    level_qty -= trade_qty
                if qty_remaining == 0:
                    break
        return trades

    def _get_orders_at_price(self, orderbook, side, price):
        # This method should be implemented in each book backend for full decoupling
        # For now, we assume the book has a method get_orders_at_price(side, price)
        if hasattr(orderbook, 'get_orders_at_price'):
            return orderbook.get_orders_at_price(side, price)
        # Fallback: try to access bids/asks dict if present
        if side == Side.BUY and hasattr(orderbook, 'bids'):
            return list(orderbook.bids.get(price, []))
        if side == Side.SELL and hasattr(orderbook, 'asks'):
            return list(orderbook.asks.get(price, []))
        return []
