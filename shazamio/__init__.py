from shazamio_core.shazamio_core import SearchParams, SignatureError

from ._endpoint import Endpoint, Settings
from ._enums import Device, GenreMusic
from ._exceptions import (
    BadPayload,
    BadResponse,
    NotFound,
    RateLimited,
    ShazamError,
    TransportError,
)
from ._middleware import CallNext, Middleware
from ._retry import Retry
from ._shazam import Shazam
from ._transport import AiohttpTransport, Request, Response, Transport
from .models import ChartTrack, ResponseTrack, TrackInfo, YoutubeData

__all__ = [
    "AiohttpTransport",
    "BadPayload",
    "BadResponse",
    "CallNext",
    "ChartTrack",
    "Device",
    "Endpoint",
    "GenreMusic",
    "Middleware",
    "NotFound",
    "RateLimited",
    "Request",
    "Response",
    "ResponseTrack",
    "Retry",
    "SearchParams",
    "Settings",
    "Shazam",
    "ShazamError",
    "SignatureError",
    "TrackInfo",
    "Transport",
    "TransportError",
    "YoutubeData",
]
