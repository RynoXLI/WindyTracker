"""
File meant to hold the TypedAPI class.

Author: Ryan Fogle
"""
from cta.simpleapi import SimpleAPI
from pydantic import validate_arguments, BaseModel, Field
from pydantic.color import Color


class TypedAPIError(Exception):
    """Error thrown when Typed API gets an unexpected response"""


class Route(BaseModel):
    id: str = Field(description="Route id")
    name: str = Field(description="Route name")
    color: Color = Field(description="Hex color")
    display: str = Field(
        description="Language-specific route designator meant for display"
    )


class Direction(BaseModel):
    id: str = Field(description="id of the direction")
    name: str = Field(description="Name of the direction")


class Location(BaseModel):
    lat: float = Field(le=90, ge=-90, description="Latitude")
    lon: float = Field(le=180, ge=-180, description="Longitude")


class Stop(BaseModel):
    id: str = Field(description="ID of stop")
    name: str = Field(description="Name of stop")
    loc: Location = Field(description="Location of the stop")


class TypedAPI:
    @validate_arguments
    def __init__(
        self,
        key,
        locale: str = "en",
        scheme: str = "https",
        domain: str = "ctabustracker.com",
    ):
        """init method

        Args:
            key (_type_): CTA API key
            locale (str, optional): language code. Defaults to "en".
            scheme (str, optional): 'https' or 'http. Defaults to "https".
            domain (str, optional): Set for different domain name. Defaults to "ctabustracker.com".
        """
        self.api = SimpleAPI(key, locale, scheme, domain)

    def get_routes(self) -> list[Route]:
        """Get all available routes.

        Raises:
            TypedAPIError: Thrown when getting an unexpected response.

        Returns:
            list[Route]: Returns a list of Routes objects.
        """
        try:
            return [
                Route(
                    id=route["rt"],
                    name=route["rtnm"],
                    color=route["rtclr"],
                    display=route["rtdd"],
                )
                for route in self.api.getroutes()["bustime-response"]["routes"]
            ]
        except KeyError as e:
            raise TypedAPIError("Unexpected API format.")

    @validate_arguments
    def get_directions(self, route: Route) -> list[Direction]:
        """Each route usually has subroutes, return these subroutes (usually denoted by N/W/S/E)

        Args:
            route (Route): Route object

        Raises:
            TypedAPIError: Thrown when getting an unexpected response.

        Returns:
            list[Direction]: Returns list of direction objects
        """
        try:
            return [
                Direction(id=direction["id"], name=direction["name"])
                for direction in self.api.getdirections(route.id)["bustime-response"][
                    "directions"
                ]
            ]
        except KeyError as e:
            raise TypedAPIError("Unexpected API format")

    @validate_arguments
    def get_stops(self, route: Route, direction: Direction) -> list[Stop]:
        """Given a route and it's direction, return the stops for the route.

        Args:
            route (Route): Route object
            direction (Direction): Direction object

        Raises:
            TypedAPIError: Thrown when getting an unexpected response.

        Returns:
            list[Stop]: Returns a list of Stop objects
        """
        try:
            return [
                Stop(
                    id=stop["stpid"],
                    name=stop["stpnm"],
                    loc=Location(lat=stop["lat"], lon=stop["long"]),
                )
                for stop in self.api.getstops(rt=route.id, direction=direction.id)[
                    "bustime-respoonse"
                ]["stops"]
            ]
        except KeyError as e:
            raise TypedAPIError("Unexpected API format.")
