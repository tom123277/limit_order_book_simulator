# Microbenchmark harness
import time
import statistics

class LatencyBench:
    def __init__(self, book, event_stream):
        self.book = book
        self.event_stream = event_stream
        self.latencies = []
        self.event_count = 0
        self.start_ns = None
        self.end_ns = None

    def run(self, warmup=100):
        # Warmup
        for i, event in enumerate(self.event_stream):
            if i >= warmup:
                break
            self._apply_event(event)
        # Reset for measurement
        self.latencies = []
        self.event_count = 0
        self.start_ns = time.perf_counter_ns()
        for event in self.event_stream:
            t0 = time.perf_counter_ns()
            self._apply_event(event)
            t1 = time.perf_counter_ns()
            self.latencies.append(t1 - t0)
            self.event_count += 1
        self.end_ns = time.perf_counter_ns()

    def _apply_event(self, event):
        etype, payload = event
        if etype == 'add':
            self.book.add_order(payload)
            self.book.match()
        elif etype == 'cancel':
            self.book.cancel_order(payload)

    def stats(self):
        if not self.latencies or self.start_ns is None or self.end_ns is None:
            return {}
        total_time = (self.end_ns - self.start_ns) / 1e9  # seconds
        throughput = self.event_count / total_time if total_time > 0 else 0
        percentiles = [50, 90, 99, 99.9]
        latency_stats = {f'p{int(p)}': statistics.quantiles(self.latencies, n=100)[int(p)-1] for p in percentiles}
        latency_stats['median'] = statistics.median(self.latencies)
        latency_stats['mean'] = statistics.mean(self.latencies)
        latency_stats['min'] = min(self.latencies)
        latency_stats['max'] = max(self.latencies)
        latency_stats['throughput'] = throughput
        latency_stats['total_events'] = self.event_count
        return latency_stats
