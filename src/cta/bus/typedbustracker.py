"""
Typed API wrapper for CTA Bus Tracker that returns Pydantic models.

Author: Ryan Fogle
"""

from typing import Union
from .bustracker import BusTracker, AsyncBusTracker
from .models import (
    TimeResponse,
    RoutesResponse,
    DirectionsResponse,
    VehiclesResponse,
    StopsResponse,
    PredictionsResponse,
    PatternsResponse,
    ServiceBulletinsResponse,
    RtpiDataFeedsResponse,
    DetoursResponse,
    AgenciesResponse,
    LocalesResponse,
    ErrorResponse,
)
from .base import BaseTypedBusTracker


class TypedBusTracker(BaseTypedBusTracker, BusTracker):
    """
    Synchronous typed version of BusTracker that returns Pydantic models instead of raw dicts.

    Example usage:
    >>> tracker = TypedBusTracker(key='secret_key')
    >>> routes = tracker.getroutes()
    >>> print(routes.routes[0].rtnm)  # Autocomplete works!
    """

    def gettime(self, unixTime: bool = False) -> Union[TimeResponse, ErrorResponse]:
        """Returns the time of the server as a typed response

        Args:
            unixTime: If true, returns unix time

        Returns:
            TimeResponse with server time or ErrorResponse if error
        """
        response = BusTracker.gettime(self, unixTime)
        return self._parse_response(response, TimeResponse)

    def getrtpidatafeeds(self) -> Union[RtpiDataFeedsResponse, ErrorResponse]:
        """Get real time passenger information feeds as typed response

        Returns:
            RtpiDataFeedsResponse with list of data feeds or ErrorResponse if error
        """
        response = BusTracker.getrtpidatafeeds(self)
        return self._parse_response(response, RtpiDataFeedsResponse)

    def getroutes(self) -> Union[RoutesResponse, ErrorResponse]:
        """Get all available routes as typed response

        Returns:
            RoutesResponse with list of routes or ErrorResponse if error
        """
        response = BusTracker.getroutes(self)
        return self._parse_response(response, RoutesResponse)

    def getdirections(self, rt: str) -> Union[DirectionsResponse, ErrorResponse]:
        """Returns available directional routes as typed response

        Args:
            rt: Route id, only accepts one

        Returns:
            DirectionsResponse with available directions or ErrorResponse if error
        """
        response = BusTracker.getdirections(self, rt)
        return self._parse_response(response, DirectionsResponse)

    def getvehicles(
        self,
        vid: str | list[str] | None = None,
        rt: str | list[str] | None = None,
        tmres: str = "s",
    ) -> Union[VehiclesResponse, ErrorResponse]:
        """Return vehicles and their real-time data as typed response

        Args:
            vid: vehicle id(s), max 10
            rt: route id(s), max 10
            tmres: time resolution, 's' for seconds, 'm' for minutes

        Returns:
            VehiclesResponse with vehicle data or ErrorResponse if error
        """
        response = BusTracker.getvehicles(self, vid, rt, tmres)
        return self._parse_response(response, VehiclesResponse)

    def getstops(
        self,
        rt: str | None = None,
        dir: str | None = None,
        stpid: str | list[str] | None = None,
    ) -> Union[StopsResponse, ErrorResponse]:
        """Returns stop information as typed response

        Args:
            rt: Route id, single route
            dir: Route direction
            stpid: stop id(s), max 10

        Returns:
            StopsResponse with stop data or ErrorResponse if error
        """
        response = BusTracker.getstops(self, rt, dir, stpid)
        return self._parse_response(response, StopsResponse)

    def getpredictions(
        self,
        stpid: str | list[str] | None = None,
        rt: str | list[str] | None = None,
        vid: str | list[str] | None = None,
        top: int | None = None,
        tmres: str = "s",
    ) -> Union[PredictionsResponse, ErrorResponse]:
        """Get real-time predictions as typed response

        Args:
            stpid: stop id(s), max 10
            rt: Optional route id(s)
            vid: vehicle id(s), max 10
            top: Maximum predictions to return
            tmres: time resolution

        Returns:
            PredictionsResponse with predictions or ErrorResponse if error
        """
        response = BusTracker.getpredictions(self, stpid, rt, vid, top, tmres)
        return self._parse_response(response, PredictionsResponse)

    def getpatterns(
        self, pid: str | list[str] | None = None, rt: str | list[str] | None = None
    ) -> Union[PatternsResponse, ErrorResponse]:
        """Return route patterns as typed response

        Args:
            pid: pattern id(s), max 10
            rt: route id(s), max 10

        Returns:
            PatternsResponse with pattern data or ErrorResponse if error
        """
        response = BusTracker.getpatterns(self, pid, rt)
        return self._parse_response(response, PatternsResponse)

    def getservicebulletins(
        self,
        rt: str | list[str] | None = None,
        rtdir: str | None = None,
        stpid: str | list[str] | None = None,
    ) -> Union[ServiceBulletinsResponse, ErrorResponse]:
        """Get service bulletins as typed response

        Args:
            rt: route id(s), max 10
            rtdir: Optional route direction
            stpid: stop id(s), max 10

        Returns:
            ServiceBulletinsResponse with bulletins or ErrorResponse if error
        """
        response = BusTracker.getservicebulletins(self, rt, rtdir, stpid)
        return self._parse_response(response, ServiceBulletinsResponse)

    def getagencies(self) -> Union[AgenciesResponse, ErrorResponse]:
        """Get agencies as typed response

        Returns:
            AgenciesResponse with agency details or ErrorResponse if error
        """
        response = BusTracker.getagencies(self)
        return self._parse_response(response, AgenciesResponse)

    def getdetours(
        self,
        rt: str | None = None,
        rtdir: str | None = None,
        rtpidatafeed: str | None = None,
    ) -> Union[DetoursResponse, ErrorResponse]:
        """Get detours as typed response

        Args:
            rt: Optional route designator (ex. '20' or 'X20')
            rtdir: Optional route direction (requires rt parameter)
            rtpidatafeed: Optional Real-Time Passenger Information data feed name (multi-feed only)

        Returns:
            DetoursResponse with detour details or ErrorResponse if error
        """
        response = BusTracker.getdetours(self, rt, rtdir, rtpidatafeed)
        return self._parse_response(response, DetoursResponse)

    def getlocalelist(
        self, inlocalLanguge: bool = False
    ) -> Union[LocalesResponse, ErrorResponse]:
        """Get locales list as typed response

        Args:
            inlocalLanguge: Display names in the native language of the locale when true

        Returns:
            LocalesResponse with available locales or ErrorResponse if error
        """
        response = BusTracker.getlocalelist(self, inlocalLanguge)
        return self._parse_response(response, LocalesResponse)


class AsyncTypedBusTracker(BaseTypedBusTracker, AsyncBusTracker):
    """
    Asynchronous typed version of AsyncBusTracker that returns Pydantic models instead of raw dicts.

    Example usage:
    >>> async with AsyncTypedBusTracker(key='secret_key') as tracker:
    ...     routes = await tracker.getroutes()
    ...     print(routes.routes[0].rtnm)  # Autocomplete works!
    """

    async def gettime(
        self, unixTime: bool = False
    ) -> Union[TimeResponse, ErrorResponse]:
        """Returns the time of the server as a typed response

        Args:
            unixTime: If true, returns unix time

        Returns:
            TimeResponse with server time or ErrorResponse if error
        """
        response = await AsyncBusTracker.gettime(self, unixTime)
        return self._parse_response(response, TimeResponse)

    async def getrtpidatafeeds(self) -> Union[RtpiDataFeedsResponse, ErrorResponse]:
        """Get real time passenger information feeds as typed response

        Returns:
            RtpiDataFeedsResponse with list of data feeds or ErrorResponse if error
        """
        response = await AsyncBusTracker.getrtpidatafeeds(self)
        return self._parse_response(response, RtpiDataFeedsResponse)

    async def getroutes(self) -> Union[RoutesResponse, ErrorResponse]:
        """Get all available routes as typed response

        Returns:
            RoutesResponse with list of routes or ErrorResponse if error
        """
        response = await AsyncBusTracker.getroutes(self)
        return self._parse_response(response, RoutesResponse)

    async def getdirections(self, rt: str) -> Union[DirectionsResponse, ErrorResponse]:
        """Returns available directional routes as typed response

        Args:
            rt: Route id, only accepts one

        Returns:
            DirectionsResponse with available directions or ErrorResponse if error
        """
        response = await AsyncBusTracker.getdirections(self, rt)
        return self._parse_response(response, DirectionsResponse)

    async def getvehicles(
        self,
        vid: str | list[str] | None = None,
        rt: str | list[str] | None = None,
        tmres: str = "s",
    ) -> Union[VehiclesResponse, ErrorResponse]:
        """Return vehicles and their real-time data as typed response

        Args:
            vid: vehicle id(s), max 10
            rt: route id(s), max 10
            tmres: time resolution, 's' for seconds, 'm' for minutes

        Returns:
            VehiclesResponse with vehicle data or ErrorResponse if error
        """
        response = await AsyncBusTracker.getvehicles(self, vid, rt, tmres)
        return self._parse_response(response, VehiclesResponse)

    async def getstops(
        self,
        rt: str | None = None,
        dir: str | None = None,
        stpid: str | list[str] | None = None,
    ) -> Union[StopsResponse, ErrorResponse]:
        """Returns stop information as typed response

        Args:
            rt: Route id, single route
            dir: Route direction
            stpid: stop id(s), max 10

        Returns:
            StopsResponse with stop data or ErrorResponse if error
        """
        response = await AsyncBusTracker.getstops(self, rt, dir, stpid)
        return self._parse_response(response, StopsResponse)

    async def getpredictions(
        self,
        stpid: str | list[str] | None = None,
        rt: str | list[str] | None = None,
        vid: str | list[str] | None = None,
        top: int | None = None,
        tmres: str = "s",
    ) -> Union[PredictionsResponse, ErrorResponse]:
        """Get real-time predictions as typed response

        Args:
            stpid: stop id(s), max 10
            rt: Optional route id(s)
            vid: vehicle id(s), max 10
            top: Maximum predictions to return
            tmres: time resolution

        Returns:
            PredictionsResponse with predictions or ErrorResponse if error
        """
        response = await AsyncBusTracker.getpredictions(
            self, stpid, rt, vid, top, tmres
        )
        return self._parse_response(response, PredictionsResponse)

    async def getpatterns(
        self, pid: str | list[str] | None = None, rt: str | list[str] | None = None
    ) -> Union[PatternsResponse, ErrorResponse]:
        """Return route patterns as typed response

        Args:
            pid: pattern id(s), max 10
            rt: route id(s), max 10

        Returns:
            PatternsResponse with pattern data or ErrorResponse if error
        """
        response = await AsyncBusTracker.getpatterns(self, pid, rt)
        return self._parse_response(response, PatternsResponse)

    async def getservicebulletins(
        self,
        rt: str | list[str] | None = None,
        rtdir: str | None = None,
        stpid: str | list[str] | None = None,
    ) -> Union[ServiceBulletinsResponse, ErrorResponse]:
        """Get service bulletins as typed response

        Args:
            rt: route id(s), max 10
            rtdir: Optional route direction
            stpid: stop id(s), max 10

        Returns:
            ServiceBulletinsResponse with bulletins or ErrorResponse if error
        """
        response = await AsyncBusTracker.getservicebulletins(self, rt, rtdir, stpid)
        return self._parse_response(response, ServiceBulletinsResponse)

    async def getagencies(self) -> Union[AgenciesResponse, ErrorResponse]:
        """Get agencies as typed response

        Returns:
            AgenciesResponse with agency details or ErrorResponse if error
        """
        response = await AsyncBusTracker.getagencies(self)
        return self._parse_response(response, AgenciesResponse)

    async def getdetours(
        self,
        rt: str | None = None,
        rtdir: str | None = None,
        rtpidatafeed: str | None = None,
    ) -> Union[DetoursResponse, ErrorResponse]:
        """Get detours as typed response

        Args:
            rt: Optional route designator (ex. '20' or 'X20')
            rtdir: Optional route direction (requires rt parameter)
            rtpidatafeed: Optional Real-Time Passenger Information data feed name (multi-feed only)

        Returns:
            DetoursResponse with detour details or ErrorResponse if error
        """
        response = await AsyncBusTracker.getdetours(self, rt, rtdir, rtpidatafeed)
        return self._parse_response(response, DetoursResponse)

    async def getlocalelist(
        self, inlocalLanguge: bool = False
    ) -> Union[LocalesResponse, ErrorResponse]:
        """Get locales list as typed response

        Args:
            inlocalLanguge: Display names in the native language of the locale when true

        Returns:
            LocalesResponse with available locales or ErrorResponse if error
        """
        response = await AsyncBusTracker.getlocalelist(self, inlocalLanguge)
        return self._parse_response(response, LocalesResponse)
