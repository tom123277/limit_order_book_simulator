import unittest
from benchmarks.trader_strategies import MarketMaker, MomentumTrader, RandomTrader
from order_book.order import Side, OrderType

class TestTraderStrategies(unittest.TestCase):
    def test_market_maker(self):
        trader = MarketMaker(1)
        order = trader.generate_order(0, 1.0)
        self.assertIn(order.side, [Side.BUY, Side.SELL])
        self.assertEqual(order.type, OrderType.LIMIT)

    def test_momentum_trader(self):
        trader = MomentumTrader(2)
        order = trader.generate_order(0, 1.0)
        self.assertIn(order.side, [Side.BUY, Side.SELL])
        self.assertEqual(order.type, OrderType.LIMIT)

    def test_random_trader(self):
        trader = RandomTrader(3)
        order = trader.generate_order(0, 1.0)
        self.assertIn(order.side, [Side.BUY, Side.SELL])
        self.assertIn(order.type, [OrderType.LIMIT, OrderType.MARKET])

if __name__ == "__main__":
    unittest.main()
