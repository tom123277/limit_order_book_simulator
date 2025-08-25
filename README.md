# Limit Order Book Simulator

A high-performance limit order book simulator and matching engine for quant/HFT research.

## Features
- Full matching engine (bids/asks, FIFO, cancels)
- Latency measurements
- Benchmarking of different data structures (`heapq`, `sortedcontainers`, custom)

## Structure
- `order_book/`: Matching engine and order book implementations
- `benchmarks/`: Benchmarking scripts and latency measurement

## Getting Started
- Install dependencies: `pip install -r requirements.txt`
- Run benchmarks: `python benchmarks/run_benchmarks.py`

## Requirements
- Python 3.8+
- `sortedcontainers` (for benchmarking)
