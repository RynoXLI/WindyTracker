"""
CTA API client for bus and train tracking.

This package provides both synchronous and asynchronous clients for the CTA (Chicago Transit Authority) API.

Installation options:
- pip install cta[sync] - For synchronous operations only (uses requests)
- pip install cta[async] - For asynchronous operations only (uses aiohttp)
- pip install cta[all] - For both synchronous and asynchronous operations
"""

# Import base classes (always available)
from cta.bus.base import BaseBusTracker
from cta.train.base import BaseTrainTracker

# Import all implementations (always available for import)
from cta.bus.bustracker import BusTracker, AsyncBusTracker
from cta.bus.typedbustracker import TypedBusTracker, AsyncTypedBusTracker
from cta.train.traintracker import TrainTracker, AsyncTrainTracker
from cta.train.typedtraintracker import TypedTrainTracker, AsyncTypedTrainTracker

__all__ = [
    "BaseBusTracker",
    "BaseTrainTracker",
    "BusTracker",
    "AsyncBusTracker",
    "TypedBusTracker",
    "AsyncTypedBusTracker",
    "TrainTracker",
    "AsyncTrainTracker",
    "TypedTrainTracker",
    "AsyncTypedTrainTracker",
]


def hello() -> str:
    return "Hello from cta!"
