"""
WindyTracker - CTA API client for bus and train tracking.

This package provides both synchronous and asynchronous clients for the CTA (Chicago Transit Authority) API.

Installation options:
- uv add cta[sync] - For synchronous operations only (uses requests)
- uv add cta[async] - For asynchronous operations only (uses aiohttp)
- uv add cta[all] - For both synchronous and asynchronous operations

Legal Notice:
Data provided by Chicago Transit Authority. WindyTracker is not affiliated with, endorsed by,
or sponsored by CTA. Use of CTA data is subject to the CTA Developer License Agreement.
"""

# Import base classes (always available)
from windytracker.bus.base import BaseBusTracker
from windytracker.train.base import BaseTrainTracker

# Import all implementations (always available for import)
from windytracker.bus.bustracker import BusTracker, AsyncBusTracker
from windytracker.bus.typedbustracker import TypedBusTracker, AsyncTypedBusTracker
from windytracker.train.traintracker import TrainTracker, AsyncTrainTracker
from windytracker.train.typedtraintracker import (
    TypedTrainTracker,
    AsyncTypedTrainTracker,
)

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
