"""
Typed API wrapper for CTA Bus Tracker that returns Pydantic models.

Author: Ryan Fogle
"""

from typing import Union
from .bustracker import BusTracker
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
from pydantic import ValidationError


class TypedBusTracker(BusTracker):
    """
    Typed version of BusTracker that returns Pydantic models instead of raw dicts.

    This provides:
    - Type safety and autocompletion
    - Runtime validation of API responses
    - Better error messages when API structure changes
    - Documentation through type hints

    Example usage:
    >>> tracker = TypedBusTracker(key='secret_key')
    >>> routes = tracker.getroutes()
    >>> print(routes.routes[0].rtnm)  # Autocomplete works!
    """

    def _parse_response(self, response_dict: dict, model_class):
        """Parse API response into typed model with error handling"""
        try:
            # CTA API wraps responses in 'bustime-response'
            bustime_data = response_dict.get("bustime-response", {})

            # Check for API errors first
            if "error" in bustime_data:
                return ErrorResponse.model_validate(bustime_data)

            return model_class.model_validate(bustime_data)
        except ValidationError as e:
            raise ValueError(f"Failed to parse API response: {e}")

    def gettime(self, unixTime: bool = False) -> Union[TimeResponse, ErrorResponse]:
        """Returns the time of the server as a typed response

        Args:
            unixTime: If true, returns unix time

        Returns:
            TimeResponse with server time or ErrorResponse if error
        """
        response = super().gettime(unixTime)
        return self._parse_response(response, TimeResponse)

    def getrtpidatafeeds(self) -> Union[RtpiDataFeedsResponse, ErrorResponse]:
        """Get real time passenger information feeds as typed response

        Returns:
            RtpiDataFeedsResponse with list of data feeds or ErrorResponse if error
        """
        response = super().getrtpidatafeeds()
        return self._parse_response(response, RtpiDataFeedsResponse)

    def getroutes(self) -> Union[RoutesResponse, ErrorResponse]:
        """Get all available routes as typed response

        Returns:
            RoutesResponse with list of routes or ErrorResponse if error
        """
        response = super().getroutes()
        return self._parse_response(response, RoutesResponse)

    def getdirections(self, rt: str) -> Union[DirectionsResponse, ErrorResponse]:
        """Returns available directional routes as typed response

        Args:
            rt: Route id, only accepts one

        Returns:
            DirectionsResponse with available directions or ErrorResponse if error
        """
        response = super().getdirections(rt)
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
        response = super().getvehicles(vid, rt, tmres)
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
        response = super().getstops(rt, dir, stpid)
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
        response = super().getpredictions(stpid, rt, vid, top, tmres)
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
        response = super().getpatterns(pid, rt)
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
        response = super().getservicebulletins(rt, rtdir, stpid)
        return self._parse_response(response, ServiceBulletinsResponse)

    def getagencies(self) -> Union[AgenciesResponse, ErrorResponse]:
        """Get agencies as typed response

        Returns:
            AgenciesResponse with agency details or ErrorResponse if error
        """
        response = super().getagencies()
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
        response = super().getdetours(rt, rtdir, rtpidatafeed)
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
        response = super().getlocalelist(inlocalLanguge)
        return self._parse_response(response, LocalesResponse)
