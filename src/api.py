import requests
from pydantic import validate_arguments
from urllib.parse import urlencode
import copy


class ApiRoutes:
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


class SimpleAPI:
    @validate_arguments
    def __init__(
        self,
        key,
        locale: str = "en",
        scheme: str = "https",
        domain: str = "ctabustracker.com",
    ):
        self._params = {"key": key, "format": "json", "locale": locale}
        self._base_url = f"{scheme}://{domain}/bustime/api/v3/"

    @validate_arguments
    def _format_url(self, subroute: str, params: dict | None = None) -> dict:
        if params is None:
            params = self._params

        return f"{self._base_url}{subroute}?{urlencode(params)}"

    def gettime(self) -> dict:
        r = requests.get(self._format_url(ApiRoutes.TIME))
        return r.json()

    def getrtpidatafeeds(self) -> dict:
        r = requests.get(self._format_url(ApiRoutes.DATA_FEEDS))
        return r.json()

    @validate_arguments
    def getvehicles(
        self,
        vid: str | list | None = None,
        rt: str | list | None = None,
        tmres: str = "s",
    ) -> dict:
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
            if len(vid) > 10:
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

        r = requests.get(self._format_url(ApiRoutes.VEHICLES, params))
        return r.json()

    def getroutes(self) -> dict:
        r = requests.get(self._format_url(ApiRoutes.ROUTES))
        return r.json()

    @validate_arguments
    def getdirections(self, rt: str) -> dict:
        params = copy.deepcopy(self._params)

        if len(rt.split(",")) > 1:
            raise ApiArgumentError("Please only provide on route (rt).")

        params["rt"] = rt
        r = requests.get(self._format_url(ApiRoutes.DIRECTIONS, params))
        return r.json()

    @validate_arguments
    def getstops(
        self,
        rt: str | None = None,
        dir: str | None = None,
        stpid: str | list | None = None,
    ) -> dict:
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

        r = requests.get(self._format_url(ApiRoutes.STOPS, params))
        return r.json()

    @validate_arguments
    def getpatterns(
        self, pid: str | list | None = None, rt: str | list | None = None
    ) -> dict:
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
        r = requests.get(self._format_url(ApiRoutes.PATTERNS, params))
        return r.json()

    @validate_arguments
    def getpredictions(
        self,
        stpid: str | list | None = None,
        rt: str | list | None = None,
        vid: str | list | None = None,
        top: int | None = None,
        tmres: str = "s",
    ) -> dict:
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

        r = requests.get(self._format_url(ApiRoutes.PREDICTIONS, params))
        return r.json()

    @validate_arguments
    def getservicebulletins(
        self,
        rt: str | list | None = None,
        rtdir: str | None = None,
        stpid: str | list | None = None,
    ) -> dict:
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
        r = requests.get(self._format_url(ApiRoutes.BULLETINS), params)
        return r.json()

    @validate_arguments
    def getlocalelist(self, inlocalLanguge: bool | None = None) -> dict:
        params = copy.deepcopy(self._params)
        if inlocalLanguge:
            params["inLocaleLanguage"] = inlocalLanguge
        r = requests.get(self._format_url(ApiRoutes.LOCALES, params))
        return r.json()

    @validate_arguments
    def getdetours(self, rt: str | None = None, rtdir: str | None = None) -> dict:
        params = copy.deepcopy(self._params)

        if rt:
            if len(rt.split(",")) > 1:
                raise ApiArgumentError("Please only provide 1 rt.")
            if rtdir:
                params["rtdir"] = rtdir
            params["rt"] = rt

        r = requests.get(self._format_url(ApiRoutes.DETOURS, params))
        return r.json()

    def getagencies(self) -> dict:
        r = requests.get(self._format_url(ApiRoutes.AGENCIES))
        return r.json()
