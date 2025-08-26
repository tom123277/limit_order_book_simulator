import unittest
from order_book.order import Order, Side, OrderType, Trade

class TestOrder(unittest.TestCase):
    def test_order_creation(self):
        order = Order(id=1, side=Side.BUY, price=100, qty=10, ts=1.0, type=OrderType.LIMIT)
        self.assertEqual(order.price, 100)
        self.assertEqual(order.qty, 10)
        self.assertEqual(order.side, Side.BUY)
        self.assertEqual(order.type, OrderType.LIMIT)

    def test_trade_creation(self):
        trade = Trade(price=100, qty=5, ts=1.0, maker_id=1, taker_id=2)
        self.assertEqual(trade.price, 100)
        self.assertEqual(trade.qty, 5)
        self.assertEqual(trade.maker_id, 1)
        self.assertEqual(trade.taker_id, 2)

class TestLimitOrderBook(unittest.TestCase):
    def setUp(self):
        from order_book.order import LimitOrderBook
        self.book = LimitOrderBook()
        self.buy1 = Order(id=1, side=Side.BUY, price=100, qty=10, ts=1.0, type=OrderType.LIMIT)
        self.sell1 = Order(id=2, side=Side.SELL, price=101, qty=5, ts=2.0, type=OrderType.LIMIT)

    def test_add_limit_and_market_order(self):
        self.book.add_order(self.buy1)
        self.assertIn(100, self.book.bids)
        market_order = Order(id=3, side=Side.BUY, price=None, qty=10, ts=3.0, type=OrderType.MARKET)
        self.book.add_order(market_order)
        self.assertNotIn(3, self.book.order_map)

    def test_cancel_nonexistent(self):
        self.assertFalse(self.book.cancel_order(999))

    def test_cancel_market_order(self):
        market_order = Order(id=4, side=Side.BUY, price=None, qty=10, ts=4.0, type=OrderType.MARKET)
        self.book.add_order(market_order)
        self.assertFalse(self.book.cancel_order(4))

    def test_cancel_limit_no_price(self):
        bad_order = Order(id=5, side=Side.BUY, price=None, qty=10, ts=5.0, type=OrderType.LIMIT)
        self.book.add_order(self.buy1)
        self.assertFalse(self.book.cancel_order(5))

    def test_cancel_after_match(self):
        self.book.add_order(self.buy1)
        sell = Order(id=6, side=Side.SELL, price=100, qty=10, ts=6.0, type=OrderType.LIMIT)
        self.book.add_order(sell)
        self.book.match()
        self.assertFalse(self.book.cancel_order(1))
        self.assertFalse(self.book.cancel_order(6))

    def test_get_orders_at_price(self):
        self.book.add_order(self.buy1)
        self.book.add_order(self.sell1)
        self.assertEqual(len(self.book.get_orders_at_price(Side.BUY, 100)), 1)
        self.assertEqual(len(self.book.get_orders_at_price(Side.SELL, 101)), 1)
        self.assertEqual(self.book.get_orders_at_price(Side.BUY, 999), [])

    def test_depth(self):
        self.book.add_order(self.buy1)
        self.book.add_order(Order(id=7, side=Side.BUY, price=99, qty=5, ts=7.0, type=OrderType.LIMIT))
        self.book.add_order(self.sell1)
        self.book.add_order(Order(id=8, side=Side.SELL, price=102, qty=3, ts=8.0, type=OrderType.LIMIT))
        depth = self.book.depth(k=2)
        self.assertEqual(len(depth['bids']), 2)
        self.assertEqual(len(depth['asks']), 2)

    def test_match_no_cross(self):
        self.book.add_order(self.buy1)
        self.book.add_order(self.sell1)
        trades = self.book.match()
        self.assertEqual(trades, [])

    def test_match_partial_and_multiple(self):
        buy = Order(id=9, side=Side.BUY, price=101, qty=10, ts=9.0, type=OrderType.LIMIT)
        sell = Order(id=10, side=Side.SELL, price=101, qty=5, ts=10.0, type=OrderType.LIMIT)
        self.book.add_order(buy)
        self.book.add_order(sell)
        trades = self.book.match()
        self.assertEqual(len(trades), 1)
        self.assertEqual(trades[0].qty, 5)
        # Add another sell to match remaining buy
        sell2 = Order(id=11, side=Side.SELL, price=101, qty=5, ts=11.0, type=OrderType.LIMIT)
        self.book.add_order(sell2)
        trades2 = self.book.match()
        self.assertEqual(len(trades2), 1)
        self.assertEqual(trades2[0].qty, 5)

if __name__ == "__main__":
    unittest.main()
