import pathlib
from io import BytesIO
from typing import Any, TypeAlias

import aiofiles
import aiohttp
from aiohttp import ContentTypeError
from pydub import AudioSegment

from shazamio.exceptions import FailedDecodeJson

SongT: TypeAlias = str | pathlib.Path | bytes | bytearray
FileT: TypeAlias = str | pathlib.Path


async def validate_json(response: aiohttp.ClientResponse) -> Any:
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
