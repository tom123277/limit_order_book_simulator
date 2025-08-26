import unittest
from sim.latency import LatencyBench
import time

class TestLatencyBench(unittest.TestCase):
    def test_latency_measurement(self):
        # Minimal stub book and event stream
        class DummyBook:
            def add_order(self, order): pass
            def match(self): pass
            def cancel_order(self, order_id): pass
        class DummyEventStream:
            def __iter__(self):
                for i in range(10):
                    yield ('add', None)
        bench = LatencyBench(DummyBook(), DummyEventStream())
        bench.run(warmup=2)
        stats = bench.stats()
        self.assertIn('mean', stats)
        self.assertIn('median', stats)
        self.assertIn('throughput', stats)

if __name__ == "__main__":
    unittest.main()
