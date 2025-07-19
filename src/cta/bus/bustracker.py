"""
File meant to hold the BusTracker API objects.

Author: Ryan Fogle
"""

import requests
import aiohttp
from abc import ABC, abstractmethod
from pydantic import validate_arguments
from urllib.parse import urlencode
import copy


class ApiRoutes:
    """Class holding all of the subroutes for the CTA HTTP URL"""

    DATA_FEEDS = "getrtpidatafeeds"
    TIME = "gettime"
    VEHICLES = "getvehicles"
    ROUTES = "getroutes"
    DIRECTIONS = "getdirections"
    STOPS = "getstops"
    PATTERNS = "getpatterns"
    PREDICTIONS = "getpredictions"
    BULLETINS = "getservicebulletins"
    LOCALES = "getlocalelist"
    DETOURS = "getdetours"
    AGENCIES = "getagencies"


class ApiArgumentError(Exception):
    """Argument raised when there is an input error"""


class BaseBusTracker(ABC):
    """Base class for CTA Bus Tracker API clients with shared validation logic."""

    @validate_arguments
    def __init__(
        self,
        key,
        locale: str = "en",
        scheme: str = "https",
        domain: str = "ctabustracker.com",
    ):
        """Initialize the base tracker.

        Args:
            key (_type_): CTA API key
            locale (str, optional): language code. Defaults to "en".
            scheme (str, optional): 'https' or 'http. Defaults to "https".
            domain (str, optional): Set for different domain name. Defaults to "ctabustracker.com".
        """
        self._params = {"key": key, "format": "json", "locale": locale}
        self._base_url = f"{scheme}://{domain}/bustime/api/v3/"

    @validate_arguments
    def _format_url(self, subroute: str, params: dict | None = None) -> str:
        """Format url for api

        Args:
            subroute (str): Subroute (ie 'getroutes', 'getdirections').
            params (dict | None, optional): GET parameters to be added. Defaults to None.

        Returns:
            str: URL
        """
        if params is None:
            params = self._params

        return f"{self._base_url}{subroute}?{urlencode(params)}"

    def _validate_getvehicles_params(self, vid, rt, tmres):
        """Validate parameters for getvehicles method."""
        params = copy.deepcopy(self._params)
        params["tmres"] = tmres

        if vid is None and rt is None:
            raise ApiArgumentError("Please only provide vid or rt argument, not both.")
        elif vid is not None and rt is not None:
            raise ApiArgumentError("Please only provide vid or rt argument, not both.")

        if isinstance(vid, list):
            if len(vid) > 10:
                raise ApiArgumentError(
                    "Please only provide 10 identifiers for vid argument."
                )
            vid = ",".join(vid)
        elif isinstance(vid, str):
            if len(vid.split(",")) > 10:
                raise ApiArgumentError(
                    "Please only provide 10 identifiers for vid argument."
                )
            params["vid"] = vid

        if isinstance(rt, list):
            if len(rt) > 10:  # Fixed: was checking len(vid) instead of len(rt)
                raise ApiArgumentError(
                    "Please only provide 10 identifiers for rt argument."
                )
            rt = ",".join(rt)
        elif isinstance(rt, str):
            if len(rt.split(",")) > 10:
                raise ApiArgumentError(
                    "Please only provide 10 identifiers for rt argument."
                )
            params["rt"] = rt

        return params

    def _validate_getdirections_params(self, rt):
        """Validate parameters for getdirections method."""
        params = copy.deepcopy(self._params)

        if len(rt.split(",")) > 1:
            raise ApiArgumentError("Please only provide on route (rt).")

        params["rt"] = rt
        return params

    def _validate_getstops_params(self, rt, dir, stpid):
        """Validate parameters for getstops method."""
        params = copy.deepcopy(self._params)

        if (rt is None and dir is None and stpid is None) or (
            (rt is not None or dir is not None) and stpid is not None
        ):
            raise ApiArgumentError(
                "Please provide either one rt and dir, or up to 10 stpids arguments."
            )
        elif stpid is not None:
            if isinstance(stpid, str):
                if len(stpid.split(",")) > 10:
                    raise ApiArgumentError("Please only provide up to 10 stpids.")
                params["stpid"] = stpid
            elif len(stpid) > 10:
                raise ApiArgumentError("Please only provide up to 10 stpids.")
            else:
                params["stpid"] = ",".join(stpid)
        elif rt is not None:
            if len(rt.split(",")) > 1:
                raise ApiArgumentError("Please only provide 1 route (rt).")
            if dir is None:
                raise ApiArgumentError("Please provide dir when also providing rt.")
            params["rt"] = rt
            params["dir"] = dir
        elif rt is None:
            raise ApiArgumentError("Please provide rt when providing dir.")

        return params

    def _validate_getpatterns_params(self, pid, rt):
        """Validate parameters for getpatterns method."""
        params = copy.deepcopy(self._params)
        if pid is None and rt is None:
            raise ApiArgumentError("Please only provide pid or rt argument.")
        elif pid is not None and rt is not None:
            raise ApiArgumentError("Please only provide pid or rt argument")
        elif pid is not None:
            if isinstance(pid, str):
                if len(pid.split(",")) > 10:
                    raise ApiArgumentError(
                        "Please only provide 10 or less pid arguments."
                    )
                params["pid"] = pid
            else:
                if len(pid) > 10:
                    raise ApiArgumentError(
                        "Please only provide 10 or less pid arguments."
                    )
                params["pid"] = ",".join(pid)
        else:
            if isinstance(rt, str):
                if len(rt.split(",")) > 10:
                    raise ApiArgumentError(
                        "Please only provide 10 or less rt arguments."
                    )
                params["rt"] = rt
            else:
                if len(rt) > 10:
                    raise ApiArgumentError(
                        "Please only provide 10 or less rt arguments."
                    )
                params["rt"] = ",".join(rt)
        return params

    def _validate_getpredictions_params(self, stpid, rt, vid, top, tmres):
        """Validate parameters for getpredictions method."""
        params = copy.deepcopy(self._params)

        if stpid is None and vid is None:
            raise ApiArgumentError("Please provide either stpid or vid arguments.")
        elif stpid is not None and vid is not None:
            raise ApiArgumentError("Please provide either stpid or vid arguments.")
        elif stpid is not None:
            if isinstance(stpid, str):
                if len(stpid.split(",")) > 10:
                    raise ApiArgumentError(
                        "Please only provide 10 or less stpid arguments."
                    )
                params["stpid"] = stpid
            else:
                if len(stpid) > 10:
                    raise ApiArgumentError(
                        "Please only provide 10 or less stpid arguments."
                    )
                params["stpid"] = ",".join(stpid)

            if rt is not None:
                params["rt"] = rt
        elif vid is not None:
            if rt is not None:
                raise ApiArgumentError("Please do not provide rt with vid")
            if isinstance(vid, str):
                if len(vid.split(",")) > 10:
                    raise ApiArgumentError(
                        "Please only provide 10 or less vid arguments."
                    )
                params["vid"] = vid
            else:
                if len(vid) > 10:
                    raise ApiArgumentError(
                        "Please only provide 10 or less vid arguments."
                    )
                params["vid"] = ",".join(vid)

        if top:
            params["top"] = top
        params["tmres"] = tmres

        return params

    def _validate_getservicebulletins_params(self, rt, rtdir, stpid):
        """Validate parameters for getservicebulletins method."""
        params = copy.deepcopy(self._params)

        if (rt is None and stpid is None) or (rt is not None and stpid is not None):
            raise ApiArgumentError("Please provide either stpid or rt arguments.")
        elif rt is not None:
            if rtdir is not None:
                if (isinstance(rt, str) and len(rt.split(",")) > 1) or (len(rt) > 1):
                    raise ApiArgumentError(
                        "Please only provide 1 rt when rtdir argument is provided."
                    )
                params["rtdir"] = rtdir

            if isinstance(rt, str):
                if len(rt.split(",")) > 10:
                    raise ApiArgumentError(
                        "Please only provide 10 or less rt arguments."
                    )
                params["rt"] = rt
            elif len(rt) > 10:
                raise ApiArgumentError("Please only provide 10 or less rt arguments.")
            else:
                params["rt"] = ",".join(rt)
        elif isinstance(stpid, str):
            if len(stpid.split(",")) > 10:
                raise ApiArgumentError(
                    "Please only provide 10 or less stpid arguments."
                )
            params["stpid"] = stpid
        elif len(stpid) > 10:
            raise ApiArgumentError("Please only provide 10 or less stpid arguments.")
        else:
            params["stpid"] = ",".join(stpid)

        return params

    def _validate_getdetours_params(self, rt, rtdir, rtpidatafeed):
        """Validate parameters for getdetours method."""
        params = copy.deepcopy(self._params)

        if rt:
            if len(rt.split(",")) > 1:
                raise ApiArgumentError("Please only provide 1 rt.")
            if rtdir:
                params["rtdir"] = rtdir
            params["rt"] = rt

        if rtpidatafeed:
            params["rtpidatafeed"] = rtpidatafeed

        return params

    # Abstract methods that must be implemented by subclasses
    @abstractmethod
    def gettime(self, unixTime=False) -> dict:
        """Returns the time of the server"""
        pass

    @abstractmethod
    def getrtpidatafeeds(self) -> dict:
        """Get real time passenger information feeds"""
        pass

    @abstractmethod
    def getvehicles(
        self,
        vid: str | list[str] | None = None,
        rt: str | list[str] | None = None,
        tmres: str = "s",
    ) -> dict:
        """Return a list of vehicles and their real-time data"""
        pass

    @abstractmethod
    def getroutes(self) -> dict:
        """Get all available routes"""
        pass

    @abstractmethod
    def getdirections(self, rt: str) -> dict:
        """Returns available directional routes"""
        pass

    @abstractmethod
    def getstops(
        self,
        rt: str | None = None,
        dir: str | None = None,
        stpid: str | list[str] | None = None,
    ) -> dict:
        """Returns semi real-time stop info"""
        pass

    @abstractmethod
    def getpatterns(
        self, pid: str | list[str] | None = None, rt: str | list[str] | None = None
    ) -> dict:
        """Return a set of points that create a pattern"""
        pass

    @abstractmethod
    def getpredictions(
        self,
        stpid: str | list[str] | None = None,
        rt: str | list[str] | None = None,
        vid: str | list[str] | None = None,
        top: int | None = None,
        tmres: str = "s",
    ) -> dict:
        """Get real-time predictions for a list of stops"""
        pass

    @abstractmethod
    def getservicebulletins(
        self,
        rt: str | list[str] | None = None,
        rtdir: str | None = None,
        stpid: str | list[str] | None = None,
    ) -> dict:
        """Get information about services for a given route or stop"""
        pass

    @abstractmethod
    def getlocalelist(self, inlocalLanguge: bool = False) -> dict:
        """Get locales list"""
        pass

    @abstractmethod
    def getdetours(
        self,
        rt: str | None = None,
        rtdir: str | None = None,
        rtpidatafeed: str | None = None,
    ) -> dict:
        """Get route detours"""
        pass

    @abstractmethod
    def getagencies(self) -> dict:
        """Get agencies"""
        pass


class BusTracker(BaseBusTracker):
    """Synchronous class built to handle validating and returning CTA responses. Very closely resembles how the API is built.

    Example usage:
    >>> cta = BusTracker(key='secret_key')
    >>> cta.getroutes()
    """

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

    async def __aenter__(self):
        """Async context manager entry."""
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
