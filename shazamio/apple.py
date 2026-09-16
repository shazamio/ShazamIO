import json
from typing import Final

from pydantic import TypeAdapter, ValidationError

from shazamio.exceptions import BadAppleIds, BadParseData

# The mapping is JSON served as `application/octet-stream`, so `response.json()`
#  raises `ContentTypeError` and the body is decoded by hand:
#  `curl -sI -A 'Dalvik/2.1.0 (Linux; U; Android 13; Pixel 7 Build/TQ3A)'
#  'https://www.shazam.com/services/sd/s/a2st/US/en-US/1125281672'`.
APPLE_TO_SHAZAM_CONTENT_TYPE: Final[str] = "application/octet-stream"

_ERROR: Final[str] = "error"
_MAPPING: Final[TypeAdapter[dict[str, str]]] = TypeAdapter(dict[str, str])


def parse_apple_to_shazam_keys(payload: str) -> dict[str, str]:
    try:
        answer = json.loads(payload)
    except json.JSONDecodeError as er:
        msg = f"Apple id mapping is not JSON: {payload[:200]}"
        raise BadParseData(msg) from er

    # A storefront the service does not serve and ids it cannot resolve are both
    #  `200 {"error":{"msg":"Could not fetch ids"}}`, so the body decides and the
    #  status says nothing.
    if isinstance(answer, dict) and _ERROR in answer:
        msg = f"Apple ids could not be resolved: {answer[_ERROR]}"
        raise BadAppleIds(msg)

    try:
        return _MAPPING.validate_python(answer)
    except ValidationError as er:
        msg = f"Apple id mapping is not a map of ids to keys: {payload[:200]}"
        raise BadParseData(msg) from er
