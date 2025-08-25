from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional

class Side(Enum):
    BUY = auto()
    SELL = auto()

class OrderType(Enum):
    LIMIT = auto()
    MARKET = auto()

@dataclass
class Order:
    id: int
    ts: float
    side: Side
    type: OrderType
    price: Optional[float]
    qty: int
    owner: Optional[str] = None
    flags: Optional[str] = None

@dataclass
class Trade:
    ts: float
    price: float
    qty: int
    maker_id: int
    taker_id: int
