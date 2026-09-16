from shazamio_core.shazamio_core import SearchParams

from .api import Shazam
from .client import HTTPClient
from .enums import GenreMusic

# `BadMethod` stays in `shazamio.exceptions`: it reports an internal invariant
#  rather than something the caller passed in, so nothing outside the package
#  has a reason to catch it.
from .exceptions import (
    BadAppleIds,
    BadCityName,
    BadCountryName,
    BadParseData,
    FailedDecodeJson,
    RateLimited,
)
from .geo import GeoService
from .schemas.charts import ChartTrack
from .serializers import Serialize

__all__ = (
    "BadAppleIds",
    "BadCityName",
    "BadCountryName",
    "BadParseData",
    "ChartTrack",
    "FailedDecodeJson",
    "GenreMusic",
    "GeoService",
    "HTTPClient",
    "RateLimited",
    "SearchParams",
    "Serialize",
    "Shazam",
)
