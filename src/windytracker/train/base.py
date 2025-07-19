"""
Base class for CTA Train Tracker API clients.

Author: Ryan Fogle
"""

from abc import ABC, abstractmethod
from pydantic import validate_arguments
from urllib.parse import urlencode
import copy
from .models import (
    CtattResponse,
    CtattFollowResponse,
    CtattPositionsResponse,
    TrainTimeResponse,
)
from pydantic import ValidationError
from typing import Union


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


class ErrorResponse(TrainTimeResponse):
    """Error response for train API"""

    errCd: str
    errNm: str


class BaseTypedTrainTracker(ABC):
    """
    Base class for typed CTA Train Tracker API clients that return Pydantic models.

    This provides:
    - Type safety and autocompletion
    - Runtime validation of API responses
    - Better error messages when API structure changes
    - Documentation through type hints
    """

    def _parse_response(self, response_dict: dict, model_class):
        """Parse API response into typed model with error handling"""
        try:
            # For JSON responses, the structure should contain 'ctatt'
            if isinstance(response_dict, dict) and "ctatt" in response_dict:
                # Check for API errors first
                ctatt_data = response_dict["ctatt"]
                if ctatt_data.get("errCd", "0") != "0":
                    error_response = ErrorResponse(
                        errCd=ctatt_data.get("errCd", "999"),
                        errNm=ctatt_data.get("errNm", "Unknown error"),
                    )
                    return error_response

                if model_class == CtattResponse:
                    return model_class.model_validate(response_dict)
                elif model_class == CtattFollowResponse:
                    return model_class.model_validate(response_dict)
                elif model_class == CtattPositionsResponse:
                    return model_class.model_validate(response_dict)
                else:
                    return model_class.model_validate(ctatt_data)
            else:
                # Handle XML responses or other formats
                return response_dict

        except ValidationError as e:
            raise ValueError(f"Failed to parse API response: {e}")

    # Abstract methods that must be implemented by subclasses
    @abstractmethod
    def arrivals(
        self,
        mapid: str | None = None,
        stpid: str | None = None,
        max: str | None = None,
        rt: str | None = None,
    ) -> Union[CtattResponse, ErrorResponse]:
        """Get arrival predictions for train stations as typed response"""
        pass

    @abstractmethod
    def follow(self, runnumber: str) -> Union[CtattFollowResponse, ErrorResponse]:
        """Follow a specific train by run number as typed response"""
        pass

    @abstractmethod
    def positions(
        self, rt: str | list[str]
    ) -> Union[CtattPositionsResponse, ErrorResponse]:
        """Get locations for trains on specified routes as typed response"""
        pass
