"""
Pydantic models for CTA Bus Tracker API responses.

Author: Ryan Fogle
"""

from pydantic import BaseModel, Field, field_validator
from typing import List, Optional
from datetime import datetime


# Base response wrapper
class BusTimeResponse(BaseModel):
    """Base wrapper for all CTA API responses"""

    pass


# Time API Models
class TimeResponse(BusTimeResponse):
    tm: datetime = Field(description="Current time as datetime object")

    @field_validator("tm", mode="before")
    @classmethod
    def parse_time_string(cls, v) -> datetime:
        """Parse CTA time string into datetime object"""
        if isinstance(v, datetime):
            return v
        if isinstance(v, str):
            try:
                # CTA format: "20250717 22:47:33"
                return datetime.strptime(v, "%Y%m%d %H:%M:%S")
            except ValueError:
                raise ValueError(f"Time must be in YYYYMMDD HH:MM:SS format, got: {v}")
        raise ValueError(f"Time must be a string or datetime, got: {type(v)}")


# Routes API Models
class Route(BaseModel):
    rt: str = Field(
        description="Alphanumeric designator of a route (ex. '20' or 'X20')"
    )
    rtnm: str = Field(
        description="Common name of the route (ex. 'Madison' for the 20 route)"
    )
    rtclr: str = Field(
        description="Color of the route line used in map (ex. '#ffffff')"
    )
    rtdd: str = Field(
        description="Language-specific route designator meant for display"
    )
    rtpidatafeed: Optional[str] = Field(
        default=None, description="Data feed name (multi-feed only)"
    )

    @field_validator("rtclr")
    @classmethod
    def validate_color(cls, v: str) -> str:
        """Validate hex color format"""
        if not v.startswith("#"):
            v = f"#{v}"
        if len(v) != 7 or not all(c in "0123456789ABCDEFabcdef" for c in v[1:]):
            raise ValueError(f"Invalid hex color format: {v}")
        return v.upper()


class RoutesResponse(BusTimeResponse):
    routes: Optional[List[Route]] = Field(default=None, description="Array of routes")
    route: Optional[List[Route]] = Field(
        default=None, description="Array of routes (alternative field name)"
    )


# Directions API Models
class Direction(BaseModel):
    id: str = Field(
        description="Direction designator that should be used in other requests such as getpredictions"
    )
    name: str = Field(
        description="Human-readable, locale-dependent name of the direction"
    )


class DirectionsResponse(BusTimeResponse):
    directions: Optional[List[Direction]] = Field(
        default=None, description="Array of directions"
    )
    dir: Optional[List[Direction]] = Field(
        default=None, description="Array of directions (alternative field name)"
    )


# Vehicles API Models
class Vehicle(BaseModel):
    vid: str = Field(description="Vehicle ID (alphanumeric bus number)")
    rtpidatafeed: Optional[str] = Field(
        default=None, description="Data feed name (multi-feed only)"
    )
    tmstmp: str = Field(
        description="Date and time of last positional update (YYYYMMDD HH:MM)"
    )
    lat: str = Field(description="Latitude position in decimal degrees (WGS 84)")
    lon: str = Field(description="Longitude position in decimal degrees (WGS 84)")
    hdg: str = Field(
        description="Heading as 360° value (0°=North, 90°=East, 180°=South, 270°=West)"
    )
    pid: int = Field(description="Pattern ID of trip currently being executed")
    pdist: int = Field(
        description="Linear distance in feet traveled into current pattern"
    )
    rt: str = Field(description="Route currently being executed (e.g. '20')")
    des: str = Field(description="Destination of current trip (e.g. 'Austin')")
    dly: Optional[bool] = Field(
        default=None, description="True if vehicle is delayed (only present if delayed)"
    )
    spd: Optional[int] = Field(
        default=None,
        description="Speed in miles per hour (MPH) as reported from vehicle",
    )
    tablockid: str = Field(description="TA's scheduled block identifier")
    tatripid: str = Field(description="TA's scheduled trip identifier")
    origtatripno: str = Field(description="Trip ID from TA scheduling system")
    zone: Optional[str] = Field(
        default="",
        description="Zone name if vehicle is in defined zone, otherwise blank",
    )
    mode: int = Field(
        description="Transportation mode (0=None, 1=Bus, 2=Ferry, 3=Rail, 4=People_Mover)"
    )
    psgld: str = Field(description="Passenger load ratio (FULL/HALF_EMPTY/EMPTY/N/A)")
    timepointid: Optional[str] = Field(
        default=None, description="Timepoint ID for current stop (GTFS support)"
    )
    sequence: Optional[int] = Field(
        default=None, description="Sequence number of current stop (GTFS support)"
    )
    stopstatus: Optional[int] = Field(
        default=None,
        description="Stop status per GTFS (0=STOPPED_AT, 1=INCOMING_AT, 2=IN_TRANSIT_TO)",
    )
    stopid: Optional[str] = Field(
        default=None, description="Stop ID for current stop (GTFS support)"
    )
    gtfsseq: Optional[int] = Field(
        default=None, description="GTFS stop sequence for current stop"
    )
    stst: int = Field(description="Scheduled start time in seconds past midnight")
    stsd: str = Field(description="Scheduled start date (yyyy-mm-dd format)")

    @field_validator("tmstmp")
    @classmethod
    def validate_timestamp(cls, v: str) -> str:
        """Validate timestamp format - supports both YYYYMMDD HH:MM and YYYYMMDD HH:MM:SS"""
        formats = ["%Y%m%d %H:%M:%S", "%Y%m%d %H:%M"]
        for fmt in formats:
            try:
                datetime.strptime(v, fmt)
                return v
            except ValueError:
                continue
        raise ValueError(
            f"Timestamp must be in YYYYMMDD HH:MM or YYYYMMDD HH:MM:SS format, got: {v}"
        )

    @field_validator("lat", "lon")
    @classmethod
    def validate_coordinates(cls, v: str) -> str:
        """Validate latitude/longitude are valid decimal degrees"""
        try:
            coord = float(v)
            return v
        except ValueError:
            raise ValueError(f"Coordinate must be a valid decimal number, got: {v}")

    @field_validator("hdg")
    @classmethod
    def validate_heading(cls, v: str) -> str:
        """Validate heading is between 0-360 degrees"""
        try:
            heading = int(v)
            if not 0 <= heading <= 360:
                raise ValueError(
                    f"Heading must be between 0-360 degrees, got: {heading}"
                )
            return v
        except ValueError as e:
            if "invalid literal" in str(e):
                raise ValueError(f"Heading must be a valid integer, got: {v}")
            raise

    @field_validator("pdist")
    @classmethod
    def validate_pattern_distance(cls, v: int) -> int:
        """Validate pattern distance is non-negative"""
        if v < 0:
            raise ValueError(f"Pattern distance must be non-negative, got: {v}")
        return v

    @field_validator("spd")
    @classmethod
    def validate_speed(cls, v: Optional[int]) -> Optional[int]:
        """Validate speed is non-negative"""
        if v is not None and v < 0:
            raise ValueError(f"Speed must be non-negative, got: {v}")
        return v

    @field_validator("mode")
    @classmethod
    def validate_mode(cls, v: int) -> int:
        """Validate transportation mode is valid"""
        if not 0 <= v <= 4:
            raise ValueError(
                f"Mode must be 0-4 (0=None, 1=Bus, 2=Ferry, 3=Rail, 4=People_Mover), got: {v}"
            )
        return v

    @field_validator("psgld")
    @classmethod
    def validate_passenger_load(cls, v: str) -> str:
        """Validate passenger load value"""
        valid_loads = ["FULL", "HALF_EMPTY", "EMPTY", "N/A"]
        if v not in valid_loads:
            raise ValueError(f"Passenger load must be one of {valid_loads}, got: {v}")
        return v

    @field_validator("stopstatus")
    @classmethod
    def validate_stop_status(cls, v: Optional[int]) -> Optional[int]:
        """Validate GTFS stop status"""
        if v is not None and v not in [0, 1, 2]:
            raise ValueError(
                f"Stop status must be 0 (STOPPED_AT), 1 (INCOMING_AT), or 2 (IN_TRANSIT_TO), got: {v}"
            )
        return v

    @field_validator("stst")
    @classmethod
    def validate_start_time(cls, v: int) -> int:
        """Validate start time is valid seconds past midnight"""
        if not 0 <= v <= 86400:  # 24 hours * 60 minutes * 60 seconds
            raise ValueError(
                f"Start time must be between 0-86400 seconds past midnight, got: {v}"
            )
        return v

    @field_validator("stsd")
    @classmethod
    def validate_service_date(cls, v: str) -> str:
        """Validate service date format yyyy-mm-dd"""
        try:
            datetime.strptime(v, "%Y-%m-%d")
            return v
        except ValueError:
            raise ValueError(f"Service date must be in yyyy-mm-dd format, got: {v}")


class VehiclesResponse(BusTimeResponse):
    vehicle: List[Vehicle]


# Stops API Models
class Stop(BaseModel):
    stpid: str = Field(description="Unique identifier representing this stop")
    stpnm: str = Field(
        description="Display name of this stop (ex. 'Madison and Clark')"
    )
    lat: float = Field(
        description="Latitude position of the stop in decimal degrees (WGS 84)"
    )
    lon: float = Field(
        description="Longitude position of the stop in decimal degrees (WGS 84)"
    )
    dtradd: Optional[List[str]] = Field(
        default=None,
        description="A list of detour ids which add (temporarily service) this stop",
    )
    dtrrem: Optional[List[str]] = Field(
        default=None,
        description="A list of detour ids which remove (detour around) this stop",
    )
    gtfsseq: Optional[int] = Field(
        default=None,
        description="Contains the GTFS stop sequence of the stop (only included if BusTime property 'developer.api.include.gtfsseq' is true and route & direction are supplied)",
    )
    ada: Optional[bool] = Field(
        default=None,
        description="True if the stop is ADA Accessible, false otherwise (only included if supplied by the TA)",
    )

    @field_validator("lat")
    @classmethod
    def validate_latitude(cls, v: float) -> float:
        """Validate latitude is within valid range"""
        if not -90 <= v <= 90:
            raise ValueError(f"Latitude must be between -90 and 90 degrees, got: {v}")
        return v

    @field_validator("lon")
    @classmethod
    def validate_longitude(cls, v: float) -> float:
        """Validate longitude is within valid range"""
        if not -180 <= v <= 180:
            raise ValueError(
                f"Longitude must be between -180 and 180 degrees, got: {v}"
            )
        return v

    @field_validator("gtfsseq")
    @classmethod
    def validate_gtfs_sequence(cls, v: Optional[int]) -> Optional[int]:
        """Validate GTFS sequence is non-negative"""
        if v is not None and v < 0:
            raise ValueError(f"GTFS sequence must be non-negative, got: {v}")
        return v


class StopsResponse(BusTimeResponse):
    stops: List[Stop]


# Predictions API Models
class Prediction(BaseModel):
    tmstmp: str = Field(
        description="Date and time (local) the prediction was generated. Date and time is represented based on the tmres parameter if the unixTime parameter is omitted or set to false. If the unixTime parameter is present and set to true, returns the number of milliseconds that have elapsed since 00:00:00 Coordinated Universal Time (UTC), Thursday, 1 January 1970"
    )
    typ: str = Field(
        description="Type of prediction. 'A' for an arrival prediction (prediction of when the vehicle will arrive at this stop). 'D' for a departure prediction (prediction of when the vehicle will depart this stop, if applicable). Predictions made for first stops of a route or layovers are examples of departure predictions"
    )
    stpid: str = Field(
        description="Unique identifier representing the stop for which this prediction was generated"
    )
    stpnm: str = Field(
        description="Display name of the stop for which this prediction was generated"
    )
    vid: str = Field(
        description="Unique ID of the vehicle for which this prediction was generated"
    )
    dstp: int = Field(
        description="Linear distance (feet) left to be traveled by the vehicle before it reaches the stop associated with this prediction"
    )
    rt: str = Field(
        description="Alphanumeric designator of the route (ex. '20' or 'X20') for which this prediction was generated"
    )
    rtdd: str = Field(
        description="Language-specific route designator meant for display"
    )
    rtdir: str = Field(
        description="Direction of travel of the route associated with this prediction (ex. 'INBOUND'). This matches the direction id seen in the getdirections call"
    )
    des: str = Field(
        description="Final destination of the vehicle associated with this prediction"
    )
    prdtm: str = Field(
        description="Predicted date and time (local) of a vehicle's arrival or departure to the stop associated with this prediction. Date and time is represented based on the tmres parameter if the unixTime parameter is omitted or set to false. If the unixTime parameter is present and set to true, returns the number of milliseconds that have elapsed since 00:00:00 Coordinated Universal Time (UTC), Thursday, 1 January 1970"
    )
    dly: Optional[bool] = Field(
        default=None,
        description="'true' if the vehicle is delayed. In version 3 this element is always present. This is not used by RTPI feeds. (Not set by CAD dynamic action 'unknown delay')",
    )
    dyn: Optional[str] = Field(
        default=None,
        description="The dynamic action type affecting this prediction. See the 'Dynamic Action Types' section for a list of possible identifiers",
    )
    tablockid: str = Field(
        description="TA's version of the scheduled block identifier for the work currently being performed by the vehicle"
    )
    tatripid: str = Field(
        description="TA's version of the scheduled trip identifier for the vehicle's current trip"
    )
    origtatripno: str = Field(description="Trip ID defined by the TA scheduling system")
    prdctdn: str = Field(
        description="This is the time left, in minutes, until the bus arrives at this stop"
    )
    zone: Optional[str] = Field(
        default=None,
        description="The zone name if the vehicle has entered a defined zones, otherwise blank. This is not used by RTPI feeds",
    )
    nbus: Optional[int] = Field(
        default=None,
        description="If this prediction is the last arrival (for this route) before a service gap, this represents the number of minutes until the next scheduled bus arrival (from the prediction time)",
    )
    psgld: Optional[str] = Field(
        default=None,
        description="String representing the ratio of the current passenger count to the vehicle's total capacity. Possible values include 'FULL', 'HALF_EMPTY', 'EMPTY' and 'N/A'. Ratios for 'FULL', 'HALF_EMPTY' and 'EMPTY' are determined by the transit agency. 'N/A' indicates that the passenger load is unknown",
    )
    gtfsseq: Optional[int] = Field(
        default=None,
        description="Contains the GTFS stop sequence of the stop for which this prediction was generated. Only included if the BusTime property 'developer.api.include.gtfsseq' is true",
    )
    stst: Optional[int] = Field(
        default=None,
        description="Contains the time (in seconds past midnight) of the scheduled start of the trip",
    )
    stsd: Optional[str] = Field(
        default=None,
        description="Contains the date (in 'yyyy-mm-dd' format) of the scheduled start of the trip",
    )
    flagstop: Optional[int] = Field(
        default=None,
        description="An integer code representing the flag-stop information for the prediction. -1 = UNDEFINED (no flag-stop information available), 0 = NORMAL (normal stop), 1 = PICKUP_AND_DISCHARGE (Flag stop for both pickup and discharge), 2 = ONLY_DISCHARGE (Flag stop for discharge only)",
    )

    @field_validator("typ")
    @classmethod
    def validate_prediction_type(cls, v: str) -> str:
        """Validate prediction type"""
        if v not in ["A", "D"]:
            raise ValueError(
                f"Prediction type must be 'A' (arrival) or 'D' (departure), got: {v}"
            )
        return v

    @field_validator("dyn", mode="before")
    @classmethod
    def validate_dynamic_action(cls, v) -> Optional[str]:
        """Validate dynamic action type identifier"""
        if v is None:
            return None

        # Convert integer to string if needed
        if isinstance(v, int):
            v = str(v)

        if isinstance(v, str):
            # Dynamic Action Types from API documentation
            valid_actions = {
                "0": "None - No change",
                "1": "Canceled - The event or trip has been canceled",
                "2": "Reassigned - The event or trip has been moved to a different work",
                "3": "Shifted - The time of this event, or the entire trip, has been moved",
                "4": 'Expressed - The event is "drop-off only" and will not stop to pick up passengers',
                "6": "Stops Affected - This trip has events that are affected by Disruption Management changes",
                "8": "New Trip - This trip was created dynamically and does not appear in the TA schedule",
                "9": "Partial Trip - This trip has been split or short-turned",
                "10": "Partial Trip New - This trip has been split with new trip identifier(s)",
                "12": "Delayed Cancel - This event or trip has been marked as canceled (not public)",
                "13": "Added Stop - This event has been added to the trip",
                "14": "Unknown Delay - This trip has been affected by a delay",
                "15": "Unknown Delay New - This dynamically created trip has been affected by a delay",
                "16": "Invalidated Trip - This trip has been invalidated",
                "17": "Invalidated Trip New - This dynamically created trip has been invalidated",
                "18": "Cancelled Trip New - This dynamically created trip has been canceled",
                "19": "Stops Affected New - This dynamically created trip has affected events",
            }
            if v not in valid_actions:
                raise ValueError(
                    f"Dynamic action type must be one of {list(valid_actions.keys())}, got: {v}"
                )
        return v

    @field_validator("dstp")
    @classmethod
    def validate_distance(cls, v: int) -> int:
        """Validate distance is non-negative"""
        if v < 0:
            raise ValueError(f"Distance must be non-negative, got: {v}")
        return v

    @field_validator("prdctdn")
    @classmethod
    def validate_countdown(cls, v: str) -> str:
        """Validate countdown format"""
        if v.lower() in ["due", "dly"]:  # Special CTA values
            return v
        try:
            minutes = int(v)
            if minutes < 0:
                raise ValueError(
                    f"Countdown minutes must be non-negative, got: {minutes}"
                )
            return v
        except ValueError:
            if v.lower() not in ["due", "dly"]:
                raise ValueError(
                    f"Countdown must be a number, 'DUE', or 'DLY', got: {v}"
                )
            return v

    @field_validator("nbus")
    @classmethod
    def validate_next_bus(cls, v: Optional[int]) -> Optional[int]:
        """Validate next bus minutes is non-negative"""
        if v is not None and v < 0:
            raise ValueError(f"Next bus minutes must be non-negative, got: {v}")
        return v

    @field_validator("psgld", mode="before")
    @classmethod
    def validate_passenger_load(cls, v) -> Optional[str]:
        """Validate passenger load value"""
        if v is None:
            return None

        # Convert to string and handle empty strings
        if isinstance(v, (int, float)):
            v = str(v)

        if isinstance(v, str):
            # Handle empty string by treating as N/A
            if v.strip() == "":
                return "N/A"

            # Valid passenger load values
            valid_loads = ["FULL", "HALF_EMPTY", "EMPTY", "N/A"]
            if v not in valid_loads:
                # If it's an unrecognized value, default to N/A
                return "N/A"

        return v

    @field_validator("gtfsseq")
    @classmethod
    def validate_gtfs_sequence(cls, v: Optional[int]) -> Optional[int]:
        """Validate GTFS sequence is non-negative"""
        if v is not None and v < 0:
            raise ValueError(f"GTFS sequence must be non-negative, got: {v}")
        return v

    @field_validator("stst")
    @classmethod
    def validate_start_time(cls, v: Optional[int]) -> Optional[int]:
        """Validate start time is valid seconds past midnight"""
        if v is not None and not 0 <= v <= 86400:  # 24 hours * 60 minutes * 60 seconds
            raise ValueError(
                f"Start time must be between 0-86400 seconds past midnight, got: {v}"
            )
        return v

    @field_validator("stsd")
    @classmethod
    def validate_service_date(cls, v: Optional[str]) -> Optional[str]:
        """Validate service date format yyyy-mm-dd"""
        if v is not None:
            try:
                datetime.strptime(v, "%Y-%m-%d")
                return v
            except ValueError:
                raise ValueError(f"Service date must be in yyyy-mm-dd format, got: {v}")
        return v

    @field_validator("flagstop")
    @classmethod
    def validate_flag_stop(cls, v: Optional[int]) -> Optional[int]:
        """Validate flag stop code"""
        if v is not None and v not in [-1, 0, 1, 2]:
            raise ValueError(
                f"Flag stop must be -1 (UNDEFINED), 0 (NORMAL), 1 (PICKUP_AND_DISCHARGE), or 2 (ONLY_DISCHARGE), got: {v}"
            )
        return v


class PredictionsResponse(BusTimeResponse):
    prd: List[Prediction]


# Patterns API Models
class PatternPoint(BaseModel):
    seq: int = Field(
        description="Position of this point in the overall sequence of points"
    )
    typ: str = Field(
        description="'S' if the point represents a Stop, 'W' if the point represents a waypoint along the route"
    )
    stpid: Optional[str] = Field(
        default=None,
        description="If the point represents a stop, the unique identifier of the stop",
    )
    stpnm: Optional[str] = Field(
        default=None,
        description="If the point represents a stop, the display name of the stop",
    )
    pdist: float = Field(
        description="If the point represents a stop, the linear distance of this point (feet) into the requested pattern"
    )
    lat: float = Field(
        description="Latitude position of the point in decimal degrees (WGS 84)"
    )
    lon: float = Field(
        description="Longitude position of the point in decimal degrees (WGS 84)"
    )

    @field_validator("seq")
    @classmethod
    def validate_sequence(cls, v: int) -> int:
        """Validate sequence is non-negative"""
        if v < 0:
            raise ValueError(f"Sequence must be non-negative, got: {v}")
        return v

    @field_validator("typ")
    @classmethod
    def validate_type(cls, v: str) -> str:
        """Validate point type"""
        if v not in ["S", "W"]:
            raise ValueError(
                f"Point type must be 'S' (stop) or 'W' (waypoint), got: {v}"
            )
        return v

    @field_validator("pdist")
    @classmethod
    def validate_distance(cls, v: float) -> float:
        """Validate distance is non-negative"""
        if v < 0:
            raise ValueError(f"Pattern distance must be non-negative, got: {v}")
        return v

    @field_validator("lat")
    @classmethod
    def validate_latitude(cls, v: float) -> float:
        """Validate latitude is within valid range"""
        if not -90 <= v <= 90:
            raise ValueError(f"Latitude must be between -90 and 90 degrees, got: {v}")
        return v

    @field_validator("lon")
    @classmethod
    def validate_longitude(cls, v: float) -> float:
        """Validate longitude is within valid range"""
        if not -180 <= v <= 180:
            raise ValueError(
                f"Longitude must be between -180 and 180 degrees, got: {v}"
            )
        return v


class DetourPoint(BaseModel):
    """Represents original pattern points for detoured patterns"""

    seq: int = Field(
        description="Position of this point in the overall sequence of points"
    )
    typ: str = Field(
        description="'S' if the point represents a Stop, 'W' if the point represents a waypoint along the route"
    )
    stpid: Optional[str] = Field(
        default=None,
        description="If the point represents a stop, the unique identifier of the stop",
    )
    stpnm: Optional[str] = Field(
        default=None,
        description="If the point represents a stop, the display name of the stop",
    )
    pdist: float = Field(
        description="If the point represents a stop, the linear distance of this point (feet) into the requested pattern"
    )
    lat: float = Field(
        description="Latitude position of the point in decimal degrees (WGS 84)"
    )
    lon: float = Field(
        description="Longitude position of the point in decimal degrees (WGS 84)"
    )

    @field_validator("seq")
    @classmethod
    def validate_sequence(cls, v: int) -> int:
        """Validate sequence is non-negative"""
        if v < 0:
            raise ValueError(f"Sequence must be non-negative, got: {v}")
        return v

    @field_validator("typ")
    @classmethod
    def validate_type(cls, v: str) -> str:
        """Validate point type"""
        if v not in ["S", "W"]:
            raise ValueError(
                f"Point type must be 'S' (stop) or 'W' (waypoint), got: {v}"
            )
        return v

    @field_validator("pdist")
    @classmethod
    def validate_distance(cls, v: float) -> float:
        """Validate distance is non-negative"""
        if v < 0:
            raise ValueError(f"Pattern distance must be non-negative, got: {v}")
        return v

    @field_validator("lat")
    @classmethod
    def validate_latitude(cls, v: float) -> float:
        """Validate latitude is within valid range"""
        if not -90 <= v <= 90:
            raise ValueError(f"Latitude must be between -90 and 90 degrees, got: {v}")
        return v

    @field_validator("lon")
    @classmethod
    def validate_longitude(cls, v: float) -> float:
        """Validate longitude is within valid range"""
        if not -180 <= v <= 180:
            raise ValueError(
                f"Longitude must be between -180 and 180 degrees, got: {v}"
            )
        return v


class Pattern(BaseModel):
    pid: int = Field(description="ID of pattern")
    ln: float = Field(description="Length of the pattern in feet")
    rtdir: str = Field(
        description="Direction that is valid for the specified route designator (e.g., 'INBOUND'). This needs to match the direction id seen in the getdirections call"
    )
    pt: List[PatternPoint] = Field(
        description="Encapsulates one a set of geo-positional points (including stops) that when connected define a pattern"
    )
    dtrid: Optional[str] = Field(
        default=None,
        description="If this pattern was created by a detour, contains the id of the detour. Does not appear for normal patterns",
    )
    dtrpt: Optional[List[DetourPoint]] = Field(
        default=None,
        description="If this pattern was created by a detour, encapsulates a set of geo-positional points that represent the original pattern. Useful for drawing dashed lines on a map",
    )

    @field_validator("pid")
    @classmethod
    def validate_pattern_id(cls, v: int) -> int:
        """Validate pattern ID is positive"""
        if v <= 0:
            raise ValueError(f"Pattern ID must be positive, got: {v}")
        return v

    @field_validator("ln")
    @classmethod
    def validate_length(cls, v: float) -> float:
        """Validate pattern length is positive"""
        if v <= 0:
            raise ValueError(f"Pattern length must be positive, got: {v}")
        return v


class PatternsResponse(BusTimeResponse):
    ptr: List[Pattern]


# Service Bulletins API Models
class ServiceAffected(BaseModel):
    """Represents one or a combination of route, direction and stop for which a service bulletin is valid"""

    rt: Optional[str] = Field(
        default=None,
        description="Alphanumeric designator of the route (ex. '20' or 'X20') for which this service bulletin is in effect",
    )
    rtdir: Optional[str] = Field(
        default=None,
        description="Direction of travel of the route for which this service bulletin is in effect. This matches the direction id seen in the getdirections call",
    )
    stpid: Optional[str] = Field(
        default=None,
        description="ID of the stop for which this service bulletin is in effect",
    )
    stpnm: Optional[str] = Field(
        default=None,
        description="Name of the stop for which this service bulletin is in effect",
    )


class ServiceBulletin(BaseModel):
    nm: str = Field(description="Unique name/identifier of the service bulletin")
    sbj: str = Field(
        description="Service bulletin subject. A short title for this service bulletin"
    )
    dtl: str = Field(
        description="Service bulletin detail. Full text of the service bulletin"
    )
    brf: str = Field(
        description="Service bulletin brief. A short text alternative to the service bulletin detail"
    )
    cse: Optional[str] = Field(default=None, description="Cause for service bulletin")
    efct: Optional[str] = Field(default=None, description="Effect for service bulletin")
    prty: str = Field(
        description="Service bulletin priority. The possible values are 'High,' 'Medium,' and 'Low'"
    )
    rtpidatafeed: Optional[str] = Field(
        default=None,
        description="(multi-feed only) The name of the data feed that the service bulletin affects. If the rtpidatafeed element is empty, the service bulletin affects the entire system",
    )
    srvc: List[ServiceAffected] = Field(
        description="Each srvc element represents one or a combination of route, direction and stop for which this service bulletin is valid. If the srvc element is empty, the service bulletin affects all routes and stops of its feed"
    )
    mod: Optional[str] = Field(
        default=None,
        description="The date/time of the last service bulletin modification in local time zone in YYYYMMDD HH:MM:SS format",
    )
    url: Optional[str] = Field(
        default=None,
        description="Contains URL to site with additional information about this service bulletin",
    )

    @field_validator("prty")
    @classmethod
    def validate_priority(cls, v: str) -> str:
        """Validate service bulletin priority"""
        valid_priorities = ["High", "Medium", "Low"]
        if v not in valid_priorities:
            raise ValueError(f"Priority must be one of {valid_priorities}, got: {v}")
        return v

    @field_validator("mod", mode="before")
    @classmethod
    def validate_modification_time(cls, v: Optional[str]) -> Optional[str]:
        """Validate modification timestamp format"""
        if v is not None:
            # Handle empty strings by returning None
            if isinstance(v, str) and not v.strip():
                return None
            try:
                datetime.strptime(v, "%Y%m%d %H:%M:%S")
                return v
            except ValueError:
                raise ValueError(
                    f"Modification time must be in YYYYMMDD HH:MM:SS format, got: {v}"
                )
        return v

    @field_validator("url")
    @classmethod
    def validate_url(cls, v: Optional[str]) -> Optional[str]:
        """Validate URL format (basic check)"""
        if v is not None and v.strip():
            # Basic URL validation - check if it looks like a URL
            if not (
                v.startswith("http://")
                or v.startswith("https://")
                or v.startswith("ftp://")
            ):
                # Allow relative URLs or other schemes
                pass
        return v


class ServiceBulletinsResponse(BusTimeResponse):
    sb: List[ServiceBulletin]


# Real Time Passenger Information (RTPI) Data Feed Models
class RtpiDataFeed(BaseModel):
    name: str = Field(
        description="Alphanumeric designator of rtpi datafeed (ex. 'Nextbus feed'). This is the value that should be used in the rtpidatafeed parameter in other requests"
    )
    source: str = Field(
        description="Origin of RTPI information. (ex. 'NEXTBUS' for the nextbus TA information)"
    )
    displayname: str = Field(
        description="TA for which this data feed returns information (ex. 'MBTA')"
    )
    enabled: bool = Field(description="True if the feed is enabled; false otherwise")
    visible: bool = Field(
        description="True if this feed may be displayed to the public; false if the feed is for internal use only"
    )

    @field_validator("enabled", "visible", mode="before")
    @classmethod
    def parse_boolean_strings(cls, v) -> bool:
        """Parse boolean values that might come as strings from the API"""
        if isinstance(v, bool):
            return v
        if isinstance(v, str):
            return v.lower() in ("true", "1", "yes", "on")
        return bool(v)


class RtpiDataFeedsResponse(BusTimeResponse):
    rtpidatafeeds: List[RtpiDataFeed] = Field(
        description="Encapsulates an external or internal data feed serviced by the system"
    )


# Detours API Models
class RouteDirection(BaseModel):
    """Represents a route and direction affected by a detour"""

    rt: str = Field(description="The designator of the route this detour is affecting")
    dir: str = Field(description="The id of the direction this detour is affecting")


class Detour(BaseModel):
    id: str = Field(
        description="The unique id of the detour. Other API calls reference these identifiers"
    )
    ver: int = Field(
        description="The version of this detour. Only the newest version of each detour is returned"
    )
    st: int = Field(
        description="The state of the detour. A value of 1 indicates the detour is active; 0 indicates a canceled detour"
    )
    desc: str = Field(description="Description of the detour")
    rtdirs: List[RouteDirection] = Field(
        description="Contains a series of rtdir elements, each with rt, the designator of the route this detour is affecting, and dir, the id of the direction this detour is affecting"
    )
    startdt: str = Field(description="The start date and time of this detour")
    enddt: str = Field(description="The end date and time of this detour")
    rtpidatafeed: Optional[str] = Field(
        default=None,
        description="(Multi-feed only) The name of the data feed that this detour was retrieved from",
    )

    @field_validator("st")
    @classmethod
    def validate_state(cls, v: int) -> int:
        """Validate detour state"""
        if v not in [0, 1]:
            raise ValueError(
                f"Detour state must be 0 (canceled) or 1 (active), got: {v}"
            )
        return v

    @field_validator("ver")
    @classmethod
    def validate_version(cls, v: int) -> int:
        """Validate version is positive"""
        if v <= 0:
            raise ValueError(f"Detour version must be positive, got: {v}")
        return v


class DetoursResponse(BusTimeResponse):
    dtr: List[Detour] = Field(
        default_factory=list, description="Encapsulates data about a detour"
    )

    @field_validator("dtr", mode="before")
    @classmethod
    def validate_detours(cls, v):
        """Handle missing or empty responses by returning empty list"""
        if v is None:
            return []
        return v


# Agencies API Models
class Agency(BaseModel):
    agencyid: Optional[int] = Field(
        default=None,
        description="Numeric identifier for the agency referenced by GTFS. The agencyid can be null and may not necessarily be unique to each agency. When null, the attribute will not be populated in the response",
    )
    shortname: str = Field(
        description="Short alphanumeric name of the agency. This also serves as a unique identifier"
    )
    longname: str = Field(
        description="The longer descriptive name of the agency. In the current implementation, longname is the same as shortname"
    )

    @field_validator("agencyid")
    @classmethod
    def validate_agency_id(cls, v: Optional[int]) -> Optional[int]:
        """Validate agency ID is positive if provided"""
        if v is not None and v <= 0:
            raise ValueError(f"Agency ID must be positive if provided, got: {v}")
        return v


class AgenciesResponse(BusTimeResponse):
    agency: List[Agency] = Field(
        description="Encapsulates details for an agency imported in the system"
    )


# Error Models
# Locales API Models
class Locale(BaseModel):
    localestring: str = Field(description="Language code identifier for the locale")
    displayname: str = Field(description="Human-readable name of the locale")


class LocalesResponse(BusTimeResponse):
    locale: List[Locale] = Field(description="List of available locales")


# Error Response Models
class ErrorMessage(BaseModel):
    msg: str = Field(description="Error message")


class ErrorResponse(BusTimeResponse):
    """
    Error response wrapper for API errors.

    Common Error Messages:
    - "No data found for parameter(s)" - No results matched given parameters
    - "Invalid parameter provided" - Parameter doesn't match any known ID
    - "Maximum number of <x> identifiers exceeded" - Too many IDs in request
    - "Invalid RTPI Data Feed parameter" - Invalid or disabled feed
    - "No RTPI Data Feed parameter provided" - Required in multi-feed systems
    - "Transaction limit for current day has been exceeded" - API quota exceeded
    - "No service scheduled" - Stop has no service scheduled
    - "No arrival times" - Stop has no scheduled arrival times

    API Version 3 Enhancements:
    - Enhanced multi-feed error handling
    - Disruption management error support
    - More specific parameter validation errors
    """

    error: List[ErrorMessage]
