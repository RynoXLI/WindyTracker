"""
File meant to hold the TrainTracker API objects for CTA train arrivals API.

Author: Ryan Fogle
"""

import requests
import aiohttp
from abc import ABC, abstractmethod
from pydantic import validate_arguments
from urllib.parse import urlencode
import copy


class ApiRoutes:
    """Class holding all of the subroutes for the CTA Train Tracker HTTP URL"""

    ARRIVALS = "ttarrivals.aspx"
    FOLLOW = "ttfollow.aspx"
    POSITIONS = "ttpositions.aspx"


class ApiArgumentError(Exception):
    """Argument raised when there is an input error"""


class BaseTrainTracker(ABC):
    """Base class for CTA Train Tracker API clients with shared validation logic."""

    @validate_arguments
    def __init__(
        self,
        key,
        scheme: str = "https",
        domain: str = "lapi.transitchicago.com",
    ):
        """Initialize the base tracker.

        Args:
            key (_type_): CTA API key
            scheme (str, optional): 'http' or 'https'. Defaults to "https".
            domain (str, optional): Set for different domain name. Defaults to "lapi.transitchicago.com".
        """
        self._params = {"key": key, "outputType": "JSON"}
        self._base_url = f"{scheme}://{domain}/api/1.0/"

    @validate_arguments
    def _format_url(self, subroute: str, params: dict | None = None) -> str:
        """Format url for api

        Args:
            subroute (str): Subroute (ie 'ttarrivals.aspx').
            params (dict | None, optional): GET parameters to be added. Defaults to None.

        Returns:
            str: URL
        """
        if params is None:
            params = self._params

        return f"{self._base_url}{subroute}?{urlencode(params)}"

    def _validate_arrivals_params(self, mapid, stpid, max, rt):
        """Validate parameters for arrivals method."""
        params = copy.deepcopy(self._params)

        if mapid is None and stpid is None:
            raise ApiArgumentError("Please provide either mapid or stpid argument.")
        elif mapid is not None and stpid is not None:
            raise ApiArgumentError(
                "Please provide either mapid or stpid argument, not both."
            )

        if mapid is not None:
            # Validate mapid is 5 digits and in 4xxxx range
            if not mapid.isdigit() or len(mapid) != 5 or not mapid.startswith("4"):
                raise ApiArgumentError(
                    "mapid must be a 5-digit number in the 4xxxx range."
                )
            params["mapid"] = mapid

        if stpid is not None:
            # Validate stpid is 5 digits and in 3xxxx range
            if not stpid.isdigit() or len(stpid) != 5 or not stpid.startswith("3"):
                raise ApiArgumentError(
                    "stpid must be a 5-digit number in the 3xxxx range."
                )
            params["stpid"] = stpid

        if max is not None:
            if not max.isdigit() or int(max) <= 0:
                raise ApiArgumentError("max must be a positive integer.")
            params["max"] = max

        if rt is not None:
            params["rt"] = rt

        return params

    def _validate_follow_params(self, runnumber):
        """Validate parameters for follow method."""
        params = copy.deepcopy(self._params)

        if not runnumber:
            raise ApiArgumentError("Please provide a run number.")

        params["runnumber"] = runnumber
        return params

    def _validate_positions_params(self, rt):
        """Validate parameters for positions method."""
        params = copy.deepcopy(self._params)

        if not rt:
            raise ApiArgumentError("Please provide at least one route.")

        if isinstance(rt, list):
            rt = ",".join(rt)

        params["rt"] = rt
        return params

    # Abstract methods that must be implemented by subclasses
    @abstractmethod
    def arrivals(
        self,
        mapid: str | None = None,
        stpid: str | None = None,
        max: str | None = None,
        rt: str | None = None,
    ) -> dict:
        """Get arrival predictions for train stations"""
        pass

    @abstractmethod
    def follow(self, runnumber: str) -> dict:
        """Follow a specific train by run number"""
        pass

    @abstractmethod
    def positions(self, rt: str | list[str]) -> dict:
        """Get locations for trains on specified routes"""
        pass


class TrainTracker(BaseTrainTracker):
    """Synchronous class built to handle validating and returning CTA train arrivals responses. Very closely resembles how the API is built.

    Example usage:
    >>> cta = TrainTracker(key='secret_key')
    >>> cta.arrivals(mapid='40380')
    """

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

    async def __aenter__(self):
        """Async context manager entry."""
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
