from shazamio_core.shazamio_core import SearchParams

from .api import Shazam
from .client import HTTPClient
from .converter import GeoService
from .enums import GenreMusic

# `BadMethod` and `BadParseData` stay in `shazamio.exceptions`: they report an
#  internal invariant rather than something the caller passed in, so nothing
#  outside the package has a reason to catch them.
from .exceptions import BadCityName, BadCountryName, BadRegionName, FailedDecodeJson
from .serializers import Serialize

__all__ = (
    "BadCityName",
    "BadCountryName",
    "BadRegionName",
    "FailedDecodeJson",
    "GenreMusic",
    "GeoService",
    "HTTPClient",
    "SearchParams",
    "Serialize",
    "Shazam",
)
