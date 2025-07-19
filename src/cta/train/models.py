"""
Pydantic models for CTA Train Tracker API responses.

Author: Ryan Fogle
"""

from pydantic import BaseModel, Field, field_validator
from typing import List, Optional
from datetime import datetime


# Base response wrapper
class TrainTimeResponse(BaseModel):
    """Base wrapper for all CTA Train API responses"""

    pass


# Arrivals API Models
class Arrival(BaseModel):
    """Individual train arrival prediction"""

    staId: str = Field(
        description="Numeric GTFS parent station ID which this prediction is for (five digits in 4xxxx range)"
    )
    stpId: str = Field(
        description="Numeric GTFS unique stop ID within station which this prediction is for (five digits in 3xxxx range)"
    )
    staNm: str = Field(description="Textual proper name of parent station")
    stpDe: str = Field(
        description="Textual description of platform for which this prediction applies"
    )
    rn: str = Field(description="Run number of train being predicted for")
    rt: str = Field(
        description="Textual, abbreviated route name of train being predicted for"
    )
    destSt: str = Field(
        description="GTFS unique stop ID where this train is expected to ultimately end its service run"
    )
    destNm: str = Field(description="Friendly destination description")
    trDr: str = Field(description="Numeric train route direction code")
    prdt: str = Field(
        description="Date-time format stamp for when the prediction was generated (YYYYMMDD HH:MM:SS)"
    )
    arrT: str = Field(
        description="Date-time format stamp for when a train is expected to arrive/depart (YYYYMMDD HH:MM:SS)"
    )
    isApp: str = Field(
        description='Indicates that Train Tracker is now declaring "Approaching" or "Due" on site for this train'
    )
    isSch: str = Field(
        description="Boolean flag to indicate whether this is a live prediction or based on schedule in lieu of live data"
    )
    isFlt: str = Field(
        description="Boolean flag to indicate whether a potential fault has been detected"
    )
    isDly: str = Field(
        description='Boolean flag to indicate whether a train is considered "delayed" in Train Tracker'
    )
    flags: Optional[str] = Field(
        default=None, description="Train flags (not presently in use)"
    )
    lat: Optional[str] = Field(
        default=None, description="Latitude position of the train in decimal degrees"
    )
    lon: Optional[str] = Field(
        default=None, description="Longitude position of the train in decimal degrees"
    )
    heading: Optional[str] = Field(
        default=None,
        description="Heading in standard bearing degrees (0=North, 90=East, 180=South, 270=West; range 0-359)",
    )

    @field_validator("staId")
    @classmethod
    def validate_station_id(cls, v: str) -> str:
        """Validate station ID is 5 digits in 4xxxx range"""
        if not v.isdigit() or len(v) != 5 or not v.startswith("4"):
            raise ValueError(f"Station ID must be 5 digits starting with 4, got: {v}")
        return v

    @field_validator("stpId")
    @classmethod
    def validate_stop_id(cls, v: str) -> str:
        """Validate stop ID is 5 digits in 3xxxx range"""
        if not v.isdigit() or len(v) != 5 or not v.startswith("3"):
            raise ValueError(f"Stop ID must be 5 digits starting with 3, got: {v}")
        return v

    @field_validator("prdt", "arrT")
    @classmethod
    def validate_datetime_format(cls, v: str) -> str:
        """Validate datetime is in correct format"""
        # Try ISO format first (what the API actually returns)
        try:
            datetime.fromisoformat(v)
            return v
        except ValueError:
            pass

        # Try the documented format as fallback
        try:
            datetime.strptime(v, "%Y%m%d %H:%M:%S")
            return v
        except ValueError:
            raise ValueError(
                f"DateTime must be in ISO format (YYYY-MM-DDTHH:MM:SS) or YYYYMMDD HH:MM:SS format, got: {v}"
            )
        return v

    @property
    def prediction_datetime(self) -> datetime:
        """Get prediction time as datetime object"""
        # Try ISO format first
        try:
            return datetime.fromisoformat(self.prdt)
        except ValueError:
            return datetime.strptime(self.prdt, "%Y%m%d %H:%M:%S")

    @property
    def arrival_datetime(self) -> datetime:
        """Get arrival time as datetime object"""
        # Try ISO format first
        try:
            return datetime.fromisoformat(self.arrT)
        except ValueError:
            return datetime.strptime(self.arrT, "%Y%m%d %H:%M:%S")

    @property
    def is_approaching(self) -> bool:
        """Check if train is approaching"""
        return self.isApp == "1"

    @property
    def is_scheduled(self) -> bool:
        """Check if prediction is schedule-based"""
        return self.isSch == "1"

    @property
    def is_delayed(self) -> bool:
        """Check if train is delayed"""
        return self.isDly == "1"

    @property
    def has_fault(self) -> bool:
        """Check if train has a potential fault"""
        return self.isFlt == "1"


class ArrivalsResponse(TrainTimeResponse):
    """Complete arrivals API response"""

    tmst: str = Field(
        description="Shows time when response was generated in format: YYYYMMDD HH:MM:SS"
    )
    errCd: str = Field(description="Numeric error code")
    errNm: Optional[str] = Field(default=None, description="Textual error description")
    eta: Optional[List[Arrival]] = Field(
        default=None, description="Container element (one per individual prediction)"
    )

    @field_validator("tmst")
    @classmethod
    def validate_timestamp(cls, v: str) -> str:
        """Validate timestamp format"""
        # Try ISO format first (what the API actually returns)
        try:
            datetime.fromisoformat(v)
            return v
        except ValueError:
            pass

        # Try the documented format as fallback
        try:
            datetime.strptime(v, "%Y%m%d %H:%M:%S")
            return v
        except ValueError:
            raise ValueError(
                f"Timestamp must be in ISO format (YYYY-MM-DDTHH:MM:SS) or YYYYMMDD HH:MM:SS format, got: {v}"
            )
        return v

    @property
    def timestamp_datetime(self) -> datetime:
        """Get response timestamp as datetime object"""
        # Try ISO format first
        try:
            return datetime.fromisoformat(self.tmst)
        except ValueError:
            return datetime.strptime(self.tmst, "%Y%m%d %H:%M:%S")

    @property
    def has_error(self) -> bool:
        """Check if response has an error"""
        return self.errCd != "0"

    @property
    def error_code(self) -> int:
        """Get error code as integer"""
        return int(self.errCd)


# Wrapper for the complete CTA response
class CtattResponse(BaseModel):
    """Root element response wrapper"""

    ctatt: ArrivalsResponse = Field(description="Root arrivals response")


# Route codes mapping (based on CTA documentation)
ROUTE_CODES = {
    "Red": "Red",
    "Blue": "Blue",
    "Brn": "Brown",
    "G": "Green",
    "Org": "Orange",
    "P": "Purple",
    "Pink": "Pink",
    "Y": "Yellow",
}

# Direction codes mapping
DIRECTION_CODES = {
    "1": "North/Inbound",
    "5": "South/Outbound",
}


# Position Model for Follow API
class Position(BaseModel):
    """Train position information"""

    lat: Optional[str] = Field(
        default=None, description="Latitude position of the train in decimal degrees"
    )
    lon: Optional[str] = Field(
        default=None, description="Longitude position of the train in decimal degrees"
    )
    heading: Optional[str] = Field(
        default=None,
        description="Heading in standard bearing degrees (0=North, 90=East, 180=South, 270=West; range 0-359)",
    )


# Follow API Response Models
class FollowResponse(TrainTimeResponse):
    """Complete follow API response"""

    tmst: str = Field(
        description="Shows time when response was generated in format: YYYYMMDD HH:MM:SS"
    )
    errCd: str = Field(description="Numeric error code")
    errNm: Optional[str] = Field(default=None, description="Textual error description")
    position: Optional[Position] = Field(
        default=None, description="Current position of the train being followed"
    )
    eta: Optional[List[Arrival]] = Field(
        default=None, description="Container element (one per individual prediction)"
    )

    @field_validator("tmst")
    @classmethod
    def validate_timestamp(cls, v: str) -> str:
        """Validate timestamp format"""
        # Try ISO format first (what the API actually returns)
        try:
            datetime.fromisoformat(v)
            return v
        except ValueError:
            pass

        # Try the documented format as fallback
        try:
            datetime.strptime(v, "%Y%m%d %H:%M:%S")
            return v
        except ValueError:
            raise ValueError(
                f"Timestamp must be in ISO format (YYYY-MM-DDTHH:MM:SS) or YYYYMMDD HH:MM:SS format, got: {v}"
            )
        return v

    @property
    def timestamp_datetime(self) -> datetime:
        """Get response timestamp as datetime object"""
        # Try ISO format first
        try:
            return datetime.fromisoformat(self.tmst)
        except ValueError:
            return datetime.strptime(self.tmst, "%Y%m%d %H:%M:%S")

    @property
    def has_error(self) -> bool:
        """Check if response has an error"""
        return self.errCd != "0"

    @property
    def error_code(self) -> int:
        """Get error code as integer"""
        return int(self.errCd)


# Wrapper for the complete CTA follow response
class CtattFollowResponse(BaseModel):
    """Root element response wrapper for follow API"""

    ctatt: FollowResponse = Field(description="Root follow response")


# Train Model for Positions API
class Train(BaseModel):
    """Individual train information for positions API"""

    rn: str = Field(description="Run number")
    destSt: str = Field(
        description="GTFS unique stop ID where this train is expected to ultimately end its service run"
    )
    destNm: str = Field(description="Friendly destination description")
    trDr: str = Field(description="Numeric train route direction code")
    nextStaId: str = Field(
        description="Next station ID (parent station ID matching GTFS)"
    )
    nextStpId: str = Field(description="Next stop ID (stop ID matching GTFS)")
    nextStaNm: str = Field(description="Proper name of next station")
    prdt: str = Field(
        description="Date-time format stamp for when the prediction was generated"
    )
    arrT: str = Field(
        description="Date-time format stamp for when a train is expected to arrive/depart"
    )
    isApp: str = Field(
        description='Indicates that Train Tracker is now declaring "Approaching" or "Due" on site for this train'
    )
    isDly: str = Field(
        description='Boolean flag to indicate whether a train is considered "delayed" in Train Tracker'
    )
    flags: Optional[str] = Field(
        default=None, description="Train flags (not presently in use)"
    )
    lat: str = Field(description="Latitude position of the train in decimal degrees")
    lon: str = Field(description="Longitude position of the train in decimal degrees")
    heading: str = Field(
        description="Heading in standard bearing degrees (0=North, 90=East, 180=South, 270=West; range 0-359)"
    )

    @field_validator("prdt", "arrT")
    @classmethod
    def validate_datetime_format(cls, v: str) -> str:
        """Validate datetime is in correct format"""
        # Try ISO format first (what the API actually returns)
        try:
            datetime.fromisoformat(v)
            return v
        except ValueError:
            pass

        # Try the documented format as fallback
        try:
            datetime.strptime(v, "%Y%m%d %H:%M:%S")
            return v
        except ValueError:
            raise ValueError(
                f"DateTime must be in ISO format (YYYY-MM-DDTHH:MM:SS) or YYYYMMDD HH:MM:SS format, got: {v}"
            )
        return v

    @property
    def prediction_datetime(self) -> datetime:
        """Get prediction time as datetime object"""
        # Try ISO format first
        try:
            return datetime.fromisoformat(self.prdt)
        except ValueError:
            return datetime.strptime(self.prdt, "%Y%m%d %H:%M:%S")

    @property
    def arrival_datetime(self) -> datetime:
        """Get arrival time as datetime object"""
        # Try ISO format first
        try:
            return datetime.fromisoformat(self.arrT)
        except ValueError:
            return datetime.strptime(self.arrT, "%Y%m%d %H:%M:%S")

    @property
    def is_approaching(self) -> bool:
        """Check if train is approaching"""
        return self.isApp == "1"

    @property
    def is_delayed(self) -> bool:
        """Check if train is delayed"""
        return self.isDly == "1"


# Route Model for Positions API
class RoutePositions(BaseModel):
    """Route with train positions"""

    name: str = Field(description="Route name", alias="@name")
    train: List[Train] = Field(description="List of trains on this route")

    class Config:
        populate_by_name = True


# Positions API Response Models
class PositionsResponse(TrainTimeResponse):
    """Complete positions API response"""

    tmst: str = Field(
        description="Shows time when response was generated in format: YYYYMMDD HH:MM:SS"
    )
    errCd: str = Field(description="Numeric error code")
    errNm: Optional[str] = Field(default=None, description="Textual error description")
    route: Optional[List[RoutePositions]] = Field(
        default=None, description="Container element (one per route in response)"
    )

    @field_validator("tmst")
    @classmethod
    def validate_timestamp(cls, v: str) -> str:
        """Validate timestamp format"""
        # Try ISO format first (what the API actually returns)
        try:
            datetime.fromisoformat(v)
            return v
        except ValueError:
            pass

        # Try the documented format as fallback
        try:
            datetime.strptime(v, "%Y%m%d %H:%M:%S")
            return v
        except ValueError:
            raise ValueError(
                f"Timestamp must be in ISO format (YYYY-MM-DDTHH:MM:SS) or YYYYMMDD HH:MM:SS format, got: {v}"
            )
        return v

    @property
    def timestamp_datetime(self) -> datetime:
        """Get response timestamp as datetime object"""
        # Try ISO format first
        try:
            return datetime.fromisoformat(self.tmst)
        except ValueError:
            return datetime.strptime(self.tmst, "%Y%m%d %H:%M:%S")

    @property
    def has_error(self) -> bool:
        """Check if response has an error"""
        return self.errCd != "0"

    @property
    def error_code(self) -> int:
        """Get error code as integer"""
        return int(self.errCd)


# Wrapper for the complete CTA positions response
class CtattPositionsResponse(BaseModel):
    """Root element response wrapper for positions API"""

    ctatt: PositionsResponse = Field(description="Root positions response")
