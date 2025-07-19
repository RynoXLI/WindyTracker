# Quick Start

Get up and running with WindyTracker in just a few minutes!

*Data provided by CTA*

## Installation

### Option 1: All Features (Recommended)
```bash
pip install cta[all]  # Includes sync + async support
```

### Option 2: Sync or Async Only
```bash
uv add windytracker[all]  # All features (recommended)
uv add windytracker[sync]   # Synchronous only
uv add windytracker[async]  # Asynchronous only
```

## Get API Key

1. Visit [CTA Developer Portal](https://www.transitchicago.com/developers/bustracker/)
2. Click "Request API Access" and fill out the form
3. Wait for approval (1-2 business days)
4. Save your API key securely

### Store API Key Safely

=== "Environment Variable (Recommended)"
    ```bash
    export CTA_API_KEY="your_api_key_here"
    ```
    
    ```python
    import os
    from windytracker import BusTracker
    
    api_key = os.getenv("CTA_API_KEY")
    tracker = BusTracker(key=api_key)
    ```

=== ".env File"
    ```env
    # .env file
    CTA_API_KEY=your_api_key_here
    ```
    
    ```python
    from dotenv import load_dotenv
    import os
    from windytracker import BusTracker
    
    load_dotenv()
    api_key = os.getenv("CTA_API_KEY")
    tracker = BusTracker(key=api_key)
    ```

## Basic Usage

### Bus Tracking

```python
from windytracker import BusTracker

# Initialize
tracker = BusTracker(key="your_api_key")

# Get all routes
routes = tracker.getroutes()

# Get predictions for a stop
predictions = tracker.getpredictions(stpid="1001")

# Get vehicles on a route
vehicles = tracker.getvehicles(rt="22")

# Get stops on a route
stops = tracker.getstops(rt="22", dir="Northbound")
```

### Train Tracking

```python
from windytracker import TrainTracker

# Initialize
tracker = TrainTracker(key="your_api_key")

# Get all train lines
lines = tracker.getroutes()

# Get arrivals at a station
arrivals = tracker.getarrivals(stpid="30001")

# Get train positions
positions = tracker.getpositions(rt="Red")
```

### Async Usage

```python
import asyncio
from windytracker import AsyncBusTracker

async def main():
    async with AsyncBusTracker(key="your_api_key") as tracker:
        # Make multiple requests concurrently
        routes_task = tracker.getroutes()
        predictions_task = tracker.getpredictions(stpid="1001")
        
        routes, predictions = await asyncio.gather(routes_task, predictions_task)
        
        print("Routes:", routes)
        print("Predictions:", predictions)

asyncio.run(main())
```

## Available Classes

| Class | Sync/Async | Raw/Pydantic | Description |
|-------|------------|--------------|-------------|
| `BusTracker` | Sync | Raw JSON | Basic synchronous bus tracking |
| `AsyncBusTracker` | Async | Raw JSON | Asynchronous bus tracking |
| `TypedBusTracker` | Sync | Pydantic | Sync bus tracking with data validation |
| `AsyncTypedBusTracker` | Async | Pydantic | Async bus tracking with data validation |
| `TrainTracker` | Sync | Raw JSON | Basic synchronous train tracking |
| `AsyncTrainTracker` | Async | Raw JSON | Asynchronous train tracking |
| `TypedTrainTracker` | Sync | Pydantic | Sync train tracking with data validation |
| `AsyncTypedTrainTracker` | Async | Pydantic | Async train tracking with data validation |

## Error Handling

```python
from windytracker import BusTracker

tracker = BusTracker(key="your_api_key")

try:
    predictions = tracker.getpredictions(stpid="1001")
    
    # Check for API errors
    if "bustime-response" in predictions:
        response = predictions["bustime-response"]
        if "error" in response:
            print(f"API Error: {response['error']}")
        else:
            prd = response.get("prd", [])
            print(f"Found {len(prd)} predictions")
            
except Exception as e:
    print(f"Request failed: {e}")
```

## Common Use Cases

### Find Next Bus
```python
def next_buses(tracker, stop_id):
    predictions = tracker.getpredictions(stpid=stop_id, top=3)
    
    if "bustime-response" in predictions:
        preds = predictions["bustime-response"].get("prd", [])
        for pred in preds:
            route = pred['rt']
            destination = pred['des'] 
            minutes = pred.get('prdctdn', 'DUE')
            print(f"Route {route} to {destination}: {minutes} min")

next_buses(tracker, "1001")
```

### Station Arrivals
```python
def station_arrivals(train_tracker, station_id):
    arrivals = train_tracker.getarrivals(stpid=station_id, max="5")
    
    if "ctatt" in arrivals:
        eta_list = arrivals["ctatt"].get("eta", [])
        for eta in eta_list:
            line = eta['rt']
            destination = eta['destNm'] 
            minutes = eta.get('min', 'Due')
            print(f"{line} Line to {destination}: {minutes}")

train_tracker = TrainTracker(key="your_api_key")
station_arrivals(train_tracker, "40380")  # Clark/Lake
```

## What's Next?

- **[Bus API Reference](api/bus.md)** - Detailed bus tracking methods
- **[Train API Reference](api/train.md)** - Detailed train tracking methods

---
**Legal Notice**: Data provided by Chicago Transit Authority. WindyTracker is not affiliated with, endorsed by, or sponsored by CTA. Use of CTA data is subject to the [CTA Developer License Agreement](https://www.transitchicago.com/developers/).
