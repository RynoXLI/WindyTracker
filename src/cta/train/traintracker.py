"""
File meant to hold the TrainTracker API objects for CTA train arrivals API.

Author: Ryan Fogle
"""

# Lazy imports with availability checks
try:
    import requests

    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False
    requests = None

try:
    import aiohttp

    HAS_AIOHTTP = True
except ImportError:
    HAS_AIOHTTP = False
    aiohttp = None

from pydantic import validate_arguments
from .base import BaseTrainTracker, ApiRoutes


class TrainTracker(BaseTrainTracker):
    """Synchronous class built to handle validating and returning CTA train arrivals responses. Very closely resembles how the API is built.

    Example usage:
    >>> cta = TrainTracker(key='secret_key')
    >>> cta.arrivals(mapid='40380')
    """

    def __init__(self, key):
        """Initialize the synchronous TrainTracker.

        Args:
            key: CTA API key

        Raises:
            ImportError: If requests is not installed.
        """
        if not HAS_REQUESTS:
            raise ImportError(
                "requests is required for synchronous operations. "
                "Install with: pip install cta[sync] or pip install cta[all]"
            )
        super().__init__(key)

    @validate_arguments
    def arrivals(
        self,
        mapid: str | None = None,
        stpid: str | None = None,
        max: str | None = None,
        rt: str | None = None,
    ) -> dict:
        """Get arrival predictions for train stations.

        Args:
            mapid (str | None): Numeric station identifier (required if stpid not specified). A single five-digit code to tell the server which station you'd like to receive predictions for. Defaults to None.
            stpid (str | None): Numeric stop identifier (required if mapid not specified). A single five-digit code to tell the server which specific stop you'd like to receive predictions for. Defaults to None.
            max (str | None, optional): Maximum number of results to return. If not specified, all available results for the requested stop or station will be returned. Defaults to None.
            rt (str | None, optional): Route code. Allows you to specify a single route for which you'd like results. Defaults to None.

        Raises:
            ApiArgumentError: Error when arguments are invalid.

        Returns:
            dict: json response
        """
        params = self._validate_arrivals_params(mapid, stpid, max, rt)
        r = requests.get(self._format_url(ApiRoutes.ARRIVALS, params))
        return r.json()

    @validate_arguments
    def follow(
        self,
        runnumber: str,
    ) -> dict:
        """Follow a specific train by run number and get all upcoming arrival predictions.

        Args:
            runnumber (str): Train run number. Allows you to specify a single run number for a train for which you'd like a series of upcoming arrival estimations.

        Raises:
            ApiArgumentError: Error when arguments are invalid.

        Returns:
            dict: json response
        """
        params = self._validate_follow_params(runnumber)
        r = requests.get(self._format_url(ApiRoutes.FOLLOW, params))
        return r.json()

    @validate_arguments
    def positions(
        self,
        rt: str | list[str],
    ) -> dict:
        """Get locations for trains on specified routes.

        Args:
            rt (str | list[str]): Train route(s). Allows you to specify one or more routes for which you'd like train location information.

        Raises:
            ApiArgumentError: Error when arguments are invalid.

        Returns:
            dict: json response
        """
        params = self._validate_positions_params(rt)
        r = requests.get(self._format_url(ApiRoutes.POSITIONS, params))
        return r.json()


class AsyncTrainTracker(BaseTrainTracker):
    """Asynchronous class built to handle validating and returning CTA train arrivals responses. Very closely resembles how the API is built.

    Example usage:
    >>> async with AsyncTrainTracker(key='secret_key') as cta:
    ...     arrivals = await cta.arrivals(mapid='40380')
    """

    def __init__(self, key):
        """Initialize the asynchronous AsyncTrainTracker.

        Args:
            key: CTA API key

        Raises:
            ImportError: If aiohttp is not installed.
        """
        if not HAS_AIOHTTP:
            raise ImportError(
                "aiohttp is required for asynchronous operations. "
                "Install with: pip install cta[async] or pip install cta[all]"
            )
        super().__init__(key)

    async def __aenter__(self):
        """Async context manager entry."""
        if not HAS_AIOHTTP:
            raise ImportError(
                "aiohttp is required for asynchronous operations. "
                "Install with: pip install cta[async] or pip install cta[all]"
            )
        self._session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if hasattr(self, "_session"):
            await self._session.close()

    @validate_arguments
    async def arrivals(
        self,
        mapid: str | None = None,
        stpid: str | None = None,
        max: str | None = None,
        rt: str | None = None,
    ) -> dict:
        """Get arrival predictions for train stations.

        Args:
            mapid (str | None): Numeric station identifier (required if stpid not specified). A single five-digit code to tell the server which station you'd like to receive predictions for. Defaults to None.
            stpid (str | None): Numeric stop identifier (required if mapid not specified). A single five-digit code to tell the server which specific stop you'd like to receive predictions for. Defaults to None.
            max (str | None, optional): Maximum number of results to return. If not specified, all available results for the requested stop or station will be returned. Defaults to None.
            rt (str | None, optional): Route code. Allows you to specify a single route for which you'd like results. Defaults to None.

        Raises:
            ApiArgumentError: Error when arguments are invalid.

        Returns:
            dict: json response
        """
        params = self._validate_arrivals_params(mapid, stpid, max, rt)
        async with self._session.get(
            self._format_url(ApiRoutes.ARRIVALS, params)
        ) as resp:
            return await resp.json()

    @validate_arguments
    async def follow(
        self,
        runnumber: str,
    ) -> dict:
        """Follow a specific train by run number and get all upcoming arrival predictions.

        Args:
            runnumber (str): Train run number. Allows you to specify a single run number for a train for which you'd like a series of upcoming arrival estimations.

        Raises:
            ApiArgumentError: Error when arguments are invalid.

        Returns:
            dict: json response
        """
        params = self._validate_follow_params(runnumber)
        async with self._session.get(
            self._format_url(ApiRoutes.FOLLOW, params)
        ) as resp:
            return await resp.json()

    @validate_arguments
    async def positions(
        self,
        rt: str | list[str],
    ) -> dict:
        """Get locations for trains on specified routes.

        Args:
            rt (str | list[str]): Train route(s). Allows you to specify one or more routes for which you'd like train location information.

        Raises:
            ApiArgumentError: Error when arguments are invalid.

        Returns:
            dict: json response
        """
        params = self._validate_positions_params(rt)
        async with self._session.get(
            self._format_url(ApiRoutes.POSITIONS, params)
        ) as resp:
            return await resp.json()
