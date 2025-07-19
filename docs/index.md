# WindyTracker

A Python library
## Get Started

1. **Get API Key**: Register at [CTA Developer Portal](https://www.transitchicago.com/developers/)
2. **Install Library**: `uv add windytracker[all]`
3. **Follow [Quick Start Guide](quickstart.md)**
4. **Check [API Reference](api/bus.md)**

---
*Data provided by Chicago Transit Authority. WindyTracker is not affiliated with, endorsed by, or sponsored by CTA.* The Chicago Transit Authority (CTA) API - track buses and trains in real-time.

*Data provided by CTA*

## Features

- **Bus & Train Tracking** - Real-time locations, predictions, and route information
- **Sync & Async** - Both synchronous and asynchronous support  
- **Typed & Untyped** - Raw JSON responses or validated Pydantic models

## Quick Install

```bash
uv add windytracker[all]    # All features
uv add windytracker[sync]   # Sync only
uv add windytracker[async]  # Async only
```

## Basic Usage

```python
from windytracker import BusTracker

# Initialize with your API key
tracker = BusTracker(key="your_api_key")

# Get bus predictions
predictions = tracker.getpredictions(stpid="1001")
```

## Get Started

1. **Get API Key**: Register at [CTA Developer Portal](https://www.transitchicago.com/developers/bustracker/)
2. **Install Library**: `pip install cta[all]`
3. **Follow [Quick Start Guide](quickstart.md)**
4. **Check [API Reference](api/bus.md)**
