# Utility functions: clocks, id gen, enums
import time
import itertools
from enum import Enum

class Side(Enum):
    BUY = 'BUY'
    SELL = 'SELL'

def now_ns():
    return time.perf_counter_ns()

def id_gen():
    return itertools.count()
