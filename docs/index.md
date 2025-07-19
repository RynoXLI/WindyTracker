# CTA Tracker

A Python library for the Chicago Transit Authority (CTA) API - track buses and trains in real-time.

## Features

- **Bus & Train Tracking** - Real-time locations, predictions, and route information
- **Sync & Async** - Both synchronous and asynchronous support  
- **Typed & Untyped** - Raw JSON responses or validated Pydantic models

## Quick Install

```bash
pip install cta[all]    # All features
pip install cta[sync]   # Sync only
pip install cta[async]  # Async only
```

## Basic Usage

```python
from cta import BusTracker

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
