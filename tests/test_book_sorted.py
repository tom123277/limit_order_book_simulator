import unittest
from order_book.book_sorted import SortedOrderBook
from order_book.order import Order, Side, OrderType

class TestSortedOrderBook(unittest.TestCase):
    def setUp(self):
        self.book = SortedOrderBook()
        self.order1 = Order(id=1, side=Side.BUY, price=100, qty=10, ts=1.0, type=OrderType.LIMIT)
        self.order2 = Order(id=2, side=Side.SELL, price=101, qty=5, ts=2.0, type=OrderType.LIMIT)

    def test_add_order(self):
        self.book.add_order(self.order1)
        self.assertTrue(len(self.book.bids) > 0)
        self.book.add_order(self.order2)
        self.assertTrue(len(self.book.asks) > 0)

    def test_cancel_order(self):
        self.book.add_order(self.order1)
        self.book.cancel_order(self.order1.id)
        self.assertTrue(len(self.book.bids) == 0)

    def test_match(self):
        # Use float prices for both orders to ensure matching
        buy_order = Order(id=1, side=Side.BUY, price=100.0, qty=10, ts=1.0, type=OrderType.LIMIT)
        sell_order = Order(id=2, side=Side.SELL, price=100.0, qty=10, ts=2.0, type=OrderType.LIMIT)
        self.book.add_order(buy_order)
        self.book.add_order(sell_order)
        trades = self.book.match()
        self.assertTrue(len(trades) > 0)

if __name__ == "__main__":
    unittest.main()
