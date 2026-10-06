from shazamio_core.shazamio_core import SearchParams, SignatureError

from .api import Shazam
from .client import HTTPClient
from .enums import GenreMusic

# `BadMethod` stays in `shazamio.exceptions`: it reports an internal invariant
#  rather than something the caller passed in, so nothing outside the package
#  has a reason to catch it. Errors `aiohttp` raises stay `aiohttp`'s to export.
from .exceptions import (
    BadAppleIds,
    BadCityName,
    BadContentType,
    BadCountryName,
    BadParseData,
    BadResponseStatus,
    FailedDecodeJson,
    RateLimited,
)
from .geo import GeoService
from .schemas.charts import ChartTrack
from .serializers import Serialize

__all__ = (
    "BadAppleIds",
    "BadCityName",
    "BadContentType",
    "BadCountryName",
    "BadParseData",
    "BadResponseStatus",
    "ChartTrack",
    "FailedDecodeJson",
    "GenreMusic",
    "GeoService",
    "HTTPClient",
    "RateLimited",
    "SearchParams",
    "Serialize",
    "Shazam",
    "SignatureError",
)
