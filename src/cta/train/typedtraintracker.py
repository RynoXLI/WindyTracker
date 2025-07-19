"""
Typed API wrapper for CTA Train Tracker that returns Pydantic models.

Author: Ryan Fogle
"""

from typing import Union
from abc import ABC, abstractmethod
from .traintracker import TrainTracker, AsyncTrainTracker
from .models import (
    CtattResponse,
    CtattFollowResponse,
    CtattPositionsResponse,
    TrainTimeResponse,
)
from pydantic import ValidationError


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


class TypedTrainTracker(BaseTypedTrainTracker, TrainTracker):
    """
    Synchronous typed version of TrainTracker that returns Pydantic models instead of raw dicts.

    Example usage:
    >>> tracker = TypedTrainTracker(key='secret_key')
    >>> arrivals = tracker.arrivals(mapid='40380')
    >>> print(arrivals.ctatt.eta[0].staNm)  # Autocomplete works!
    """

    def arrivals(
        self,
        mapid: str | None = None,
        stpid: str | None = None,
        max: str | None = None,
        rt: str | None = None,
    ) -> Union[CtattResponse, ErrorResponse]:
        """Get arrival predictions for train stations as typed response

        Args:
            mapid: Numeric station identifier (required if stpid not specified)
            stpid: Numeric stop identifier (required if mapid not specified)
            max: Maximum number of results to return (as string)
            rt: Route code for filtering results

        Returns:
            CtattResponse with arrival predictions or ErrorResponse if error
        """
        response = TrainTracker.arrivals(self, mapid, stpid, max, rt)
        return self._parse_response(response, CtattResponse)

    def follow(
        self,
        runnumber: str,
    ) -> Union[CtattFollowResponse, ErrorResponse]:
        """Follow a specific train by run number as typed response

        Args:
            runnumber: Train run number for which to get upcoming arrival predictions

        Returns:
            CtattFollowResponse with train position and arrival predictions or ErrorResponse if error
        """
        response = TrainTracker.follow(self, runnumber)
        return self._parse_response(response, CtattFollowResponse)

    def positions(
        self,
        rt: str | list[str],
    ) -> Union[CtattPositionsResponse, ErrorResponse]:
        """Get locations for trains on specified routes as typed response

        Args:
            rt: Train route(s) for which to get train location information

        Returns:
            CtattPositionsResponse with train locations or ErrorResponse if error
        """
        response = TrainTracker.positions(self, rt)
        return self._parse_response(response, CtattPositionsResponse)


class AsyncTypedTrainTracker(BaseTypedTrainTracker, AsyncTrainTracker):
    """
    Asynchronous typed version of AsyncTrainTracker that returns Pydantic models instead of raw dicts.

    Example usage:
    >>> async with AsyncTypedTrainTracker(key='secret_key') as tracker:
    ...     arrivals = await tracker.arrivals(mapid='40380')
    ...     print(arrivals.ctatt.eta[0].staNm)  # Autocomplete works!
    """

    async def arrivals(
        self,
        mapid: str | None = None,
        stpid: str | None = None,
        max: str | None = None,
        rt: str | None = None,
    ) -> Union[CtattResponse, ErrorResponse]:
        """Get arrival predictions for train stations as typed response

        Args:
            mapid: Numeric station identifier (required if stpid not specified)
            stpid: Numeric stop identifier (required if mapid not specified)
            max: Maximum number of results to return (as string)
            rt: Route code for filtering results

        Returns:
            CtattResponse with arrival predictions or ErrorResponse if error
        """
        response = await AsyncTrainTracker.arrivals(self, mapid, stpid, max, rt)
        return self._parse_response(response, CtattResponse)

    async def follow(
        self,
        runnumber: str,
    ) -> Union[CtattFollowResponse, ErrorResponse]:
        """Follow a specific train by run number as typed response

        Args:
            runnumber: Train run number for which to get upcoming arrival predictions

        Returns:
            CtattFollowResponse with train position and arrival predictions or ErrorResponse if error
        """
        response = await AsyncTrainTracker.follow(self, runnumber)
        return self._parse_response(response, CtattFollowResponse)

    async def positions(
        self,
        rt: str | list[str],
    ) -> Union[CtattPositionsResponse, ErrorResponse]:
        """Get locations for trains on specified routes as typed response

        Args:
            rt: Train route(s) for which to get train location information

        Returns:
            CtattPositionsResponse with train locations or ErrorResponse if error
        """
        response = await AsyncTrainTracker.positions(self, rt)
        return self._parse_response(response, CtattPositionsResponse)
