# WindyTracker

A Python library for the Chicago Transit Authority (CTA) API - track buses and trains in real-time.

*Data provided by CTA*

[![PyPI version](https://badge.fury.io/py/windytracker.svg)](https://badge.fury.io/py/windytracker)
[![Python 3.13+](https://img.shields.io/badge/python-3.13+-blue.svg)](https://www.python.org/downloads/)

## Features

- 🚌 **Bus Tracking** - Real-time bus locations, predictions, and routes
- 🚊 **Train Tracking** - L train arrivals, positions, and station info
- ⚡ **Async Support** - Both synchronous and asynchronous operations
- 📝 **Type Safety** - Optional Pydantic models for data validation
- 🔧 **Simple API** - Easy-to-use interface matching CTA's official API

## Quick Start

### Installation

```bash
uv add windytracker[all]    # All features (recommended)
uv add windytracker[sync]   # Sync only
uv add windytracker[async]  # Async only
```

Or with pip:
```bash
pip install windytracker[all]
```

### Get API Key

1. Register at [CTA Developer Portal](https://www.transitchicago.com/developers/)
2. Request API access and wait for approval

### Basic Usage

```python
from windytracker import BusTracker

# Initialize with your API key
tracker = BusTracker(key="your_api_key")

# Get next buses at a stop
predictions = tracker.getpredictions(stpid="1001")

# Get all routes
routes = tracker.getroutes()
```

### Async Usage

```python
import asyncio
from windytracker import AsyncBusTracker

async def main():
    async with AsyncBusTracker(key="your_api_key") as tracker:
        predictions = await tracker.getpredictions(stpid="1001")
        print(predictions)

asyncio.run(main())
```

## Available Classes

| Class | Sync/Async | Raw/Pydantic | Use Case |
|-------|------------|--------------|----------|
| `BusTracker` | Sync | Raw JSON | Simple bus tracking |
| `AsyncBusTracker` | Async | Raw JSON | Async bus tracking |
| `TypedBusTracker` | Sync | Pydantic | Type-safe bus tracking |
| `TrainTracker` | Sync | Raw JSON | Simple train tracking |
| `AsyncTrainTracker` | Async | Raw JSON | Async train tracking |
| `TypedTrainTracker` | Sync | Pydantic | Type-safe train tracking |

## Documentation

Full documentation is available at: [https://rynoxli.github.io/windytracker](https://rynoxli.github.io/windytracker)

## Development

```bash
git clone https://github.com/RynoXLI/windytracker.git
cd windytracker
uv sync --all-extras
```

### Run Documentation Locally

```bash
uv run mkdocs serve
```

## License

This project is subject to the [CTA Developer License Agreement](https://www.transitchicago.com/developers/).

Data provided by Chicago Transit Authority. WindyTracker is not affiliated with, endorsed by, or sponsored by CTA.

## Contributing

Contributions welcome! Please see our contributing guidelines.
