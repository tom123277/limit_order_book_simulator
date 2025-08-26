# Microbenchmark harness
import time
import statistics
from order_book.order import Trade

class LatencyBench:
    def __init__(self, book, event_stream):
        self.book = book
        self.event_stream = event_stream
        self.latencies = []
        self.insert_latencies = []
        self.cancel_latencies = []
        self.match_latencies = []
        self.trade_emit_latencies = []
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
        self.insert_latencies = []
        self.cancel_latencies = []
        self.match_latencies = []
        self.trade_emit_latencies = []
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
            t0 = time.perf_counter_ns()
            self.book.add_order(payload)
            t1 = time.perf_counter_ns()
            self.insert_latencies.append(t1 - t0)

            t2 = time.perf_counter_ns()
            trades = self.book.match()
            t3 = time.perf_counter_ns()
            self.match_latencies.append(t3 - t2)

            # Trade emit: time for creating Trade objects (if any)
            if trades:
                for trade in trades:
                    # Simulate trade emit as time to instantiate Trade
                    t_emit0 = time.perf_counter_ns()
                    _ = Trade(trade.ts, trade.price, trade.qty, trade.maker_id, trade.taker_id)
                    t_emit1 = time.perf_counter_ns()
                    self.trade_emit_latencies.append(t_emit1 - t_emit0)
        elif etype == 'cancel':
            t0 = time.perf_counter_ns()
            self.book.cancel_order(payload)
            t1 = time.perf_counter_ns()
            self.cancel_latencies.append(t1 - t0)

    def stats(self):
        def stage_stats(latencies):
            if not latencies:
                return {}
            percentiles = [50, 90, 99, 99.9]
            stats = {f'p{int(p)}': statistics.quantiles(latencies, n=100)[int(p)-1] for p in percentiles}
            stats['median'] = statistics.median(latencies)
            stats['mean'] = statistics.mean(latencies)
            stats['min'] = min(latencies)
            stats['max'] = max(latencies)
            return stats

        if not self.latencies or self.start_ns is None or self.end_ns is None:
            return {}
        total_time = (self.end_ns - self.start_ns) / 1e9  # seconds
        throughput = self.event_count / total_time if total_time > 0 else 0
        return {
            'overall': stage_stats(self.latencies),
            'insert': stage_stats(self.insert_latencies),
            'cancel': stage_stats(self.cancel_latencies),
            'match': stage_stats(self.match_latencies),
            'trade_emit': stage_stats(self.trade_emit_latencies),
            'throughput': throughput,
            'total_events': self.event_count
        }

    def pretty_report(self):
        stats = self.stats()
        def print_stage(stage, label):
            s = stats.get(stage, {})
            if not s:
                print(f"{label}: No data")
                return
            print(f"{label}:")
            for p in ['p50', 'p90', 'p99', 'p99.9', 'median', 'mean', 'min', 'max']:
                if p in s:
                    print(f"  {p}: {s[p]:.2f} ns")
        print("Latency Percentiles by Stage:")
        print_stage('insert', 'Insert')
        print_stage('cancel', 'Cancel')
        print_stage('match', 'Match')
        print_stage('trade_emit', 'Trade Emit')
        print_stage('overall', 'Overall')
        print(f"Throughput: {stats.get('throughput', 0):.2f} events/sec")
        print(f"Total Events: {stats.get('total_events', 0)}")
