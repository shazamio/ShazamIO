from shazamio_core.shazamio_core import SearchParams, SignatureError

from .api import Shazam
from .client import HTTPClient
from .enums import Device, GenreMusic
from .exceptions import (
    BadPayload,
    BadResponse,
    NotFound,
    RateLimited,
    ShazamError,
)
from .geo import GeoService
from .schemas.charts import ChartTrack
from .schemas.models import ResponseTrack, TrackInfo, YoutubeData
from .serializers import Serialize

__all__ = [
    "BadPayload",
    "BadResponse",
    "ChartTrack",
    "Device",
    "GenreMusic",
    "GeoService",
    "HTTPClient",
    "NotFound",
    "RateLimited",
    "ResponseTrack",
    "SearchParams",
    "Serialize",
    "Shazam",
    "ShazamError",
    "SignatureError",
    "TrackInfo",
    "YoutubeData",
]
