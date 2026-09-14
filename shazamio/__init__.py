from shazamio_core.shazamio_core import SearchParams

from .api import Shazam
from .client import HTTPClient

# `BadMethod` and `BadParseData` stay in `shazamio.exceptions`: they report an
#  internal invariant rather than something the caller passed in, so nothing
#  outside the package has a reason to catch them.
from .exceptions import FailedDecodeJson
from .serializers import Serialize

__all__ = (
    "FailedDecodeJson",
    "HTTPClient",
    "SearchParams",
    "Serialize",
    "Shazam",
)
