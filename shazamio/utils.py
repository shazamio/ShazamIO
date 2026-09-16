import pathlib
from http import HTTPStatus
from io import BytesIO
from typing import Any, TypeAlias

import aiofiles
import aiohttp
from aiohttp import ContentTypeError
from pydub import AudioSegment

from shazamio.exceptions import FailedDecodeJson, RateLimited

SongT: TypeAlias = str | pathlib.Path | bytes | bytearray
FileT: TypeAlias = str | pathlib.Path


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


async def get_file_bytes(file: FileT) -> bytes:
    async with aiofiles.open(file, mode="rb") as f:
        return await f.read()


async def get_song(data: SongT) -> AudioSegment:
    if isinstance(data, (str, pathlib.Path)):
        song_bytes = await get_file_bytes(file=data)
        return AudioSegment.from_file(BytesIO(song_bytes))

    if isinstance(data, (bytes, bytearray)):
        return AudioSegment.from_file(BytesIO(data))

    if isinstance(data, AudioSegment):
        return data

    msg = f"Unsupported data type: {type(data)}"
    raise TypeError(msg)
