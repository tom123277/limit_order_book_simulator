
import numpy as np
import random
from typing import Iterator, Optional, Tuple, Union
from lob.order import Order, Side, OrderType

class SyntheticEventStream:
    def __init__(self, n_events=10000, mid_start=100.0, drift=0.0001, sigma=0.01, cancel_prob=0.1, seed: Optional[int]=42):
        self.n_events = n_events
        self.mid = mid_start
        self.drift = drift
        self.sigma = sigma
        self.cancel_prob = cancel_prob
        self.rng = np.random.default_rng(seed)
        self.order_id_gen = self._id_gen()
        self.active_orders = []

    def _id_gen(self):
        i = 1
        while True:
            yield i
            i += 1

    def __iter__(self) -> Iterator[Tuple[str, Union[Order, int]]]:
        for _ in range(self.n_events):
            # Poisson arrival
            dt = self.rng.exponential(1.0)
            self.mid += self.drift + self.rng.normal(0, self.sigma)
            ts = dt
            # Decide cancel or new order
            if self.active_orders and random.random() < self.cancel_prob:
                cancel_order = random.choice(self.active_orders)
                yield ('cancel', cancel_order.id)
                continue
            side = Side.BUY if random.random() < 0.5 else Side.SELL
            order_type = OrderType.LIMIT if random.random() < 0.9 else OrderType.MARKET
            price = None
            if order_type == OrderType.LIMIT:
                price = round(self.mid + self.rng.normal(0, 0.05) * (1 if side == Side.BUY else -1), 2)
            qty = int(self.rng.lognormal(mean=1.5, sigma=0.5))
            order = Order(
                id=next(self.order_id_gen),
                ts=ts,
                side=side,
                type=order_type,
                price=price,
                qty=qty
            )
            self.active_orders.append(order)
            yield ('add', order)
