"""
File meant to hold the BusTracker API objects.

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
import copy
from .base import BaseBusTracker, ApiRoutes


class BusTracker(BaseBusTracker):
    """Synchronous class built to handle validating and returning CTA responses. Very closely resembles how the API is built.

    Example usage:
    >>> cta = BusTracker(key='secret_key')
    >>> cta.getroutes()
    """

    def __init__(
        self,
        key,
        locale: str = "en",
        scheme: str = "https",
        domain: str = "ctabustracker.com",
    ):
        """Initialize the synchronous BusTracker.

        Args:
            key: CTA API key
            locale (str, optional): language code. Defaults to "en".
            scheme (str, optional): 'https' or 'http. Defaults to "https".
            domain (str, optional): Set for different domain name. Defaults to "ctabustracker.com".

        Raises:
            ImportError: If requests is not installed.
        """
        if not HAS_REQUESTS:
            raise ImportError(
                "requests is required for synchronous operations. "
                "Install with: pip install cta[sync] or pip install cta[all]"
            )
        super().__init__(key, locale, scheme, domain)

    def gettime(self, unixTime=False) -> dict:
        """Returns the time of the server

        Args:
            unixTime (bool, optional): If true, returns unix time. Defaults to False.

        Returns:
            dict: json response
        """
        params = copy.deepcopy(self._params)
        if unixTime:
            params["unixTime"] = unixTime
        r = requests.get(self._format_url(ApiRoutes.TIME, params))
        return r.json()

    def getrtpidatafeeds(self) -> dict:
        """Get real time passenger information feeds

        Returns:
            dict: json response
        """
        r = requests.get(self._format_url(ApiRoutes.DATA_FEEDS))
        return r.json()

    @validate_arguments
    def getvehicles(
        self,
        vid: str | list[str] | None = None,
        rt: str | list[str] | None = None,
        tmres: str = "s",
    ) -> dict:
        """Return a list of vehicles and their real-time data. Only vehicle id (vid) or route id (rt) can be passed.

        Args:
            vid (str | list[str] | None): vehicle id, can be a comma delimited string of vehicle ids or a list of vehicles ids. No more than 10 vehicle ids can be accepted. Defaults to None.
            rt (str | list[str] | None): route id, can be comma delimited string of routes or a list of routes. No more than 10 routes can be accepted. Defaults to None.
            tmres (str, optional): time resolution, 's' for seconds, 'm' for minutes. Defaults to "s".

        Raises:
            ApiArgumentError: Error when the arguments are invalid.

        Returns:
            dict: json response
        """
        params = self._validate_getvehicles_params(vid, rt, tmres)
        r = requests.get(self._format_url(ApiRoutes.VEHICLES, params))
        return r.json()

    def getroutes(self) -> dict:
        """Get all available routes

        Returns:
            dict: json response
        """
        r = requests.get(self._format_url(ApiRoutes.ROUTES))
        return r.json()

    @validate_arguments
    def getdirections(self, rt: str) -> dict:
        """Returns available directional routes

        Args:
            rt (str): Route id, only accepts one.

        Raises:
            ApiArgumentError: Error when arguments are invalid.

        Returns:
            dict: json response
        """
        params = self._validate_getdirections_params(rt)
        r = requests.get(self._format_url(ApiRoutes.DIRECTIONS, params))
        return r.json()

    @validate_arguments
    def getstops(
        self,
        rt: str | None = None,
        dir: str | None = None,
        stpid: str | list[str] | None = None,
    ) -> dict:
        """Returns semi real-time stop info. Only Route id (rt) or stop id (stpid) can be passed.

        Args:
            rt (str | None): Route id, single route, required if stpid is not provided. Defaults to None.
            dir (str | None): Route direction, required if route is provided. Defaults to None.
            stpid (str | list[str] | None): stop id, can be comma delimited string of stops or a list of stops. No more than 10 stops can be accepted. Defaults to None.

        Raises:
            ApiArgumentError: Error when arguments are invalid.

        Returns:
            dict: json response
        """
        params = self._validate_getstops_params(rt, dir, stpid)
        r = requests.get(self._format_url(ApiRoutes.STOPS, params))
        return r.json()

    @validate_arguments
    def getpatterns(
        self, pid: str | list[str] | None = None, rt: str | list[str] | None = None
    ) -> dict:
        """Return a set of points that create a pattern

        Args:
            pid (str | list[str] | None): pattern id, required if route (rt) parameter is not provided. Can be comma delimitated string of patterns, or list of patterns. Defaults to None.
            rt (str | list[str] | None): route id, required if patterns (pid) are not provided, only accepts one. Defaults to None.

        Raises:
            ApiArgumentError: Error when arguments are invalid.

        Returns:
            dict: _description_
        """
        params = self._validate_getpatterns_params(pid, rt)
        r = requests.get(self._format_url(ApiRoutes.PATTERNS, params))
        return r.json()

    @validate_arguments
    def getpredictions(
        self,
        stpid: str | list[str] | None = None,
        rt: str | list[str] | None = None,
        vid: str | list[str] | None = None,
        top: int | None = None,
        tmres: str = "s",
    ) -> dict:
        """Get real-time predictions for a list of stops.

        Args:
            stpid (str | list[str] | None, optional): stop id, can be a string of comma delimited stops, or a list of routes. Required if vehicle id (vid) is not provided. Defaults to None.
            rt (str | list[str] | None, optional): Optional route id can be provided with stops. can be a string of comma delimited stops, or a list of stops. Defaults to None.
            vid (str | list[str] | None, optional): Vehicle id, can be a string of comma delimited vehicles or a list of vehicles. Required if stop id (stpid) is not provided. Defaults to None.
            top (int | None, optional): Maximum number of predictions to be returned. Defaults to None.
            tmres (str, optional): time resolution, 's' for seconds, 'm' for minutes. Defaults to "s".

        Raises:
            ApiArgumentError: Error when arguments are invalid.

        Returns:
            dict: json response
        """
        params = self._validate_getpredictions_params(stpid, rt, vid, top, tmres)
        r = requests.get(self._format_url(ApiRoutes.PREDICTIONS, params))
        return r.json()

    @validate_arguments
    def getservicebulletins(
        self,
        rt: str | list[str] | None = None,
        rtdir: str | None = None,
        stpid: str | list[str] | None = None,
    ) -> dict:
        """Get information about services for a given route or stop.

        Args:
            rt (str | list[str] | None, optional): route id, can be a comma delimited list of routes or a list of routes, required if stop id (stpid) are not provided. If combed with rmdir, only one route can be specified. Defaults to None.
            rtdir (str | None, optional): Optional single route direction. Defaults to None.
            stpid (str | list[str] | None, optional): stop id, can be a comma delimited list of stops or a list of stops, required if routes (rt) are not provided. Defaults to None.

        Raises:
            ApiArgumentError: Errors when arguments are invalid.

        Returns:
            dict: json response
        """
        params = self._validate_getservicebulletins_params(rt, rtdir, stpid)
        r = requests.get(self._format_url(ApiRoutes.BULLETINS, params))
        return r.json()

    @validate_arguments
    def getlocalelist(self, inlocalLanguge: bool = False) -> dict:
        """Get locales list

        Args:
            inlocalLanguge (bool): Display names in the native language of the locale when true. Defaults to False.

        Returns:
            dict: json response
        """
        params = copy.deepcopy(self._params)
        if inlocalLanguge:
            params["inLocaleLanguage"] = inlocalLanguge
        r = requests.get(self._format_url(ApiRoutes.LOCALES, params))
        return r.json()

    @validate_arguments
    def getdetours(
        self,
        rt: str | None = None,
        rtdir: str | None = None,
        rtpidatafeed: str | None = None,
    ) -> dict:
        """Get route detours.

        Args:
            rt (str | None): route id, single route only. Defaults to None.
            rtdir (str | None, optional): Optional route direction. Defaults to None.
            rtpidatafeed (str | None, optional): Real-Time Passenger Information data feed name (multi-feed only). Required in multi-feed systems if rt parameter is provided. Defaults to None.

        Raises:
            ApiArgumentError: Errors when arguments are invalid.

        Returns:
            dict: json response
        """
        params = self._validate_getdetours_params(rt, rtdir, rtpidatafeed)
        r = requests.get(self._format_url(ApiRoutes.DETOURS, params))
        return r.json()

    def getagencies(self) -> dict:
        r = requests.get(self._format_url(ApiRoutes.AGENCIES))
        return r.json()


class AsyncBusTracker(BaseBusTracker):
    """Asynchronous class built to handle validating and returning CTA responses. Very closely resembles how the API is built.

    Example usage:
    >>> async with AsyncBusTracker(key='secret_key') as cta:
    ...     routes = await cta.getroutes()
    """

    def __init__(
        self,
        key,
        locale: str = "en",
        scheme: str = "https",
        domain: str = "ctabustracker.com",
    ):
        """Initialize the asynchronous AsyncBusTracker.

        Args:
            key: CTA API key
            locale (str, optional): language code. Defaults to "en".
            scheme (str, optional): 'https' or 'http. Defaults to "https".
            domain (str, optional): Set for different domain name. Defaults to "ctabustracker.com".

        Raises:
            ImportError: If aiohttp is not installed.
        """
        if not HAS_AIOHTTP:
            raise ImportError(
                "aiohttp is required for asynchronous operations. "
                "Install with: pip install cta[async] or pip install cta[all]"
            )
        super().__init__(key, locale, scheme, domain)

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

    async def gettime(self, unixTime=False) -> dict:
        """Returns the time of the server

        Args:
            unixTime (bool, optional): If true, returns unix time. Defaults to False.

        Returns:
            dict: json response
        """
        params = copy.deepcopy(self._params)
        if unixTime:
            params["unixTime"] = unixTime

        async with self._session.get(self._format_url(ApiRoutes.TIME, params)) as resp:
            return await resp.json()

    async def getrtpidatafeeds(self) -> dict:
        """Get real time passenger information feeds

        Returns:
            dict: json response
        """
        async with self._session.get(self._format_url(ApiRoutes.DATA_FEEDS)) as resp:
            return await resp.json()

    @validate_arguments
    async def getvehicles(
        self,
        vid: str | list[str] | None = None,
        rt: str | list[str] | None = None,
        tmres: str = "s",
    ) -> dict:
        """Return a list of vehicles and their real-time data. Only vehicle id (vid) or route id (rt) can be passed.

        Args:
            vid (str | list[str] | None): vehicle id, can be a comma delimited string of vehicle ids or a list of vehicles ids. No more than 10 vehicle ids can be accepted. Defaults to None.
            rt (str | list[str] | None): route id, can be comma delimited string of routes or a list of routes. No more than 10 routes can be accepted. Defaults to None.
            tmres (str, optional): time resolution, 's' for seconds, 'm' for minutes. Defaults to "s".

        Raises:
            ApiArgumentError: Error when the arguments are invalid.

        Returns:
            dict: json response
        """
        params = self._validate_getvehicles_params(vid, rt, tmres)
        async with self._session.get(
            self._format_url(ApiRoutes.VEHICLES, params)
        ) as resp:
            return await resp.json()

    async def getroutes(self) -> dict:
        """Get all available routes

        Returns:
            dict: json response
        """
        async with self._session.get(self._format_url(ApiRoutes.ROUTES)) as resp:
            return await resp.json()

    @validate_arguments
    async def getdirections(self, rt: str) -> dict:
        """Returns available directional routes

        Args:
            rt (str): Route id, only accepts one.

        Raises:
            ApiArgumentError: Error when arguments are invalid.

        Returns:
            dict: json response
        """
        params = self._validate_getdirections_params(rt)
        async with self._session.get(
            self._format_url(ApiRoutes.DIRECTIONS, params)
        ) as resp:
            return await resp.json()

    @validate_arguments
    async def getstops(
        self,
        rt: str | None = None,
        dir: str | None = None,
        stpid: str | list[str] | None = None,
    ) -> dict:
        """Returns semi real-time stop info. Only Route id (rt) or stop id (stpid) can be passed.

        Args:
            rt (str | None): Route id, single route, required if stpid is not provided. Defaults to None.
            dir (str | None): Route direction, required if route is provided. Defaults to None.
            stpid (str | list[str] | None): stop id, can be comma delimited string of stops or a list of stops. No more than 10 stops can be accepted. Defaults to None.

        Raises:
            ApiArgumentError: Error when arguments are invalid.

        Returns:
            dict: json response
        """
        params = self._validate_getstops_params(rt, dir, stpid)
        async with self._session.get(self._format_url(ApiRoutes.STOPS, params)) as resp:
            return await resp.json()

    @validate_arguments
    async def getpatterns(
        self, pid: str | list[str] | None = None, rt: str | list[str] | None = None
    ) -> dict:
        """Return a set of points that create a pattern

        Args:
            pid (str | list[str] | None): pattern id, required if route (rt) parameter is not provided. Can be comma delimitated string of patterns, or list of patterns. Defaults to None.
            rt (str | list[str] | None): route id, required if patterns (pid) are not provided, only accepts one. Defaults to None.

        Raises:
            ApiArgumentError: Error when arguments are invalid.

        Returns:
            dict: _description_
        """
        params = self._validate_getpatterns_params(pid, rt)
        async with self._session.get(
            self._format_url(ApiRoutes.PATTERNS, params)
        ) as resp:
            return await resp.json()

    @validate_arguments
    async def getpredictions(
        self,
        stpid: str | list[str] | None = None,
        rt: str | list[str] | None = None,
        vid: str | list[str] | None = None,
        top: int | None = None,
        tmres: str = "s",
    ) -> dict:
        """Get real-time predictions for a list of stops.

        Args:
            stpid (str | list[str] | None, optional): stop id, can be a string of comma delimited stops, or a list of routes. Required if vehicle id (vid) is not provided. Defaults to None.
            rt (str | list[str] | None, optional): Optional route id can be provided with stops. can be a string of comma delimited stops, or a list of stops. Defaults to None.
            vid (str | list[str] | None, optional): Vehicle id, can be a string of comma delimited vehicles or a list of vehicles. Required if stop id (stpid) is not provided. Defaults to None.
            top (int | None, optional): Maximum number of predictions to be returned. Defaults to None.
            tmres (str, optional): time resolution, 's' for seconds, 'm' for minutes. Defaults to "s".

        Raises:
            ApiArgumentError: Error when arguments are invalid.

        Returns:
            dict: json response
        """
        params = self._validate_getpredictions_params(stpid, rt, vid, top, tmres)
        async with self._session.get(
            self._format_url(ApiRoutes.PREDICTIONS, params)
        ) as resp:
            return await resp.json()

    @validate_arguments
    async def getservicebulletins(
        self,
        rt: str | list[str] | None = None,
        rtdir: str | None = None,
        stpid: str | list[str] | None = None,
    ) -> dict:
        """Get information about services for a given route or stop.

        Args:
            rt (str | list[str] | None, optional): route id, can be a comma delimited list of routes or a list of routes, required if stop id (stpid) are not provided. If combed with rmdir, only one route can be specified. Defaults to None.
            rtdir (str | None, optional): Optional single route direction. Defaults to None.
            stpid (str | list[str] | None, optional): stop id, can be a comma delimited list of stops or a list of stops, required if routes (rt) are not provided. Defaults to None.

        Raises:
            ApiArgumentError: Errors when arguments are invalid.

        Returns:
            dict: json response
        """
        params = self._validate_getservicebulletins_params(rt, rtdir, stpid)
        async with self._session.get(
            self._format_url(ApiRoutes.BULLETINS, params)
        ) as resp:
            return await resp.json()

    @validate_arguments
    async def getlocalelist(self, inlocalLanguge: bool = False) -> dict:
        """Get locales list

        Args:
            inlocalLanguge (bool): Display names in the native language of the locale when true. Defaults to False.

        Returns:
            dict: json response
        """
        params = copy.deepcopy(self._params)
        if inlocalLanguge:
            params["inLocaleLanguage"] = inlocalLanguge
        async with self._session.get(
            self._format_url(ApiRoutes.LOCALES, params)
        ) as resp:
            return await resp.json()

    @validate_arguments
    async def getdetours(
        self,
        rt: str | None = None,
        rtdir: str | None = None,
        rtpidatafeed: str | None = None,
    ) -> dict:
        """Get route detours.

        Args:
            rt (str | None): route id, single route only. Defaults to None.
            rtdir (str | None, optional): Optional route direction. Defaults to None.
            rtpidatafeed (str | None, optional): Real-Time Passenger Information data feed name (multi-feed only). Required in multi-feed systems if rt parameter is provided. Defaults to None.

        Raises:
            ApiArgumentError: Errors when arguments are invalid.

        Returns:
            dict: json response
        """
        params = self._validate_getdetours_params(rt, rtdir, rtpidatafeed)
        async with self._session.get(
            self._format_url(ApiRoutes.DETOURS, params)
        ) as resp:
            return await resp.json()

    async def getagencies(self) -> dict:
        async with self._session.get(self._format_url(ApiRoutes.AGENCIES)) as resp:
            return await resp.json()
