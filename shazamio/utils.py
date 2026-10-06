from http import HTTPStatus
from typing import Any

import aiohttp
from aiohttp import ContentTypeError

from shazamio.exceptions import FailedDecodeJson, RateLimited


async def validate_json(response: aiohttp.ClientResponse) -> Any:
    # A throttled request carries no payload to decode, so without this it
    #  surfaces as `FailedDecodeJson` below: a message naming the parser for
    #  something the rate limiter did. `SongRec` reports the status by name too:
    #  https://github.com/marin-m/SongRec/blob/b94ee61d51f40e8b3051da8f5c6a9e9c437b3633/src/core/fingerprinting/communication.rs#L120
    if response.status == HTTPStatus.TOO_MANY_REQUESTS:
        msg = f"{response.url} rate limited the request"
        raise RateLimited(msg)

    try:
        return await response.json()
    except ContentTypeError as er:
        body = await response.text()
        msg = f"Failed to decode json (status={response.status}): {body[:200]}"
        raise FailedDecodeJson(msg) from er
