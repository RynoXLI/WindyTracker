"""
Base class for CTA Bus Tracker API clients.

Author: Ryan Fogle
"""

from abc import ABC, abstractmethod
from pydantic import validate_arguments
from urllib.parse import urlencode
import copy
from typing import Union
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


class BaseTypedBusTracker(ABC):
    """
    Base class for typed CTA Bus Tracker API clients that return Pydantic models.

    This provides:
    - Type safety and autocompletion
    - Runtime validation of API responses
    - Better error messages when API structure changes
    - Documentation through type hints
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

    # Abstract methods that must be implemented by subclasses
    @abstractmethod
    def gettime(self, unixTime: bool = False) -> Union[TimeResponse, ErrorResponse]:
        """Returns the time of the server as a typed response"""
        pass

    @abstractmethod
    def getrtpidatafeeds(self) -> Union[RtpiDataFeedsResponse, ErrorResponse]:
        """Get real time passenger information feeds as typed response"""
        pass

    @abstractmethod
    def getroutes(self) -> Union[RoutesResponse, ErrorResponse]:
        """Get all available routes as typed response"""
        pass

    @abstractmethod
    def getdirections(self, rt: str) -> Union[DirectionsResponse, ErrorResponse]:
        """Returns available directional routes as typed response"""
        pass

    @abstractmethod
    def getvehicles(
        self,
        vid: str | list[str] | None = None,
        rt: str | list[str] | None = None,
        tmres: str = "s",
    ) -> Union[VehiclesResponse, ErrorResponse]:
        """Return vehicles and their real-time data as typed response"""
        pass

    @abstractmethod
    def getstops(
        self,
        rt: str | None = None,
        dir: str | None = None,
        stpid: str | list[str] | None = None,
    ) -> Union[StopsResponse, ErrorResponse]:
        """Returns stop information as typed response"""
        pass

    @abstractmethod
    def getpredictions(
        self,
        stpid: str | list[str] | None = None,
        rt: str | list[str] | None = None,
        vid: str | list[str] | None = None,
        top: int | None = None,
        tmres: str = "s",
    ) -> Union[PredictionsResponse, ErrorResponse]:
        """Get real-time predictions as typed response"""
        pass

    @abstractmethod
    def getpatterns(
        self, pid: str | list[str] | None = None, rt: str | list[str] | None = None
    ) -> Union[PatternsResponse, ErrorResponse]:
        """Return route patterns as typed response"""
        pass

    @abstractmethod
    def getservicebulletins(
        self,
        rt: str | list[str] | None = None,
        rtdir: str | None = None,
        stpid: str | list[str] | None = None,
    ) -> Union[ServiceBulletinsResponse, ErrorResponse]:
        """Get service bulletins as typed response"""
        pass

    @abstractmethod
    def getagencies(self) -> Union[AgenciesResponse, ErrorResponse]:
        """Get agencies as typed response"""
        pass

    @abstractmethod
    def getdetours(
        self,
        rt: str | None = None,
        rtdir: str | None = None,
        rtpidatafeed: str | None = None,
    ) -> Union[DetoursResponse, ErrorResponse]:
        """Get detours as typed response"""
        pass

    @abstractmethod
    def getlocalelist(
        self, inlocalLanguge: bool = False
    ) -> Union[LocalesResponse, ErrorResponse]:
        """Get locales list as typed response"""
        pass
