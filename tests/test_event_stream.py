import unittest
from sim.event_stream import SyntheticEventStream
from order_book.order import Order, Side, OrderType

class TestSyntheticEventStream(unittest.TestCase):
    def test_stream_generation(self):
        stream = SyntheticEventStream(n_events=10)
        events = list(stream)
        self.assertTrue(len(events) > 0)
        for event in events:
            self.assertIn(event[0], ('add', 'cancel'))
            if event[0] == 'add':
                from lob.order import Order
                self.assertIsInstance(event[1], Order)

if __name__ == "__main__":
    unittest.main()
