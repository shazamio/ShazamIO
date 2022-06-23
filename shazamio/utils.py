import pathlib
from typing import Union
from pydub import AudioSegment
from io import BytesIO

import aiofiles
import aiohttp
from aiohttp import ContentTypeError
from shazamio.exceptions import FailedDecodeJson

SongT = Union[str, pathlib.Path, bytes, bytearray]
FileT = Union[str, pathlib.Path]


async def validate_json(
    resp: aiohttp.ClientResponse, content_type: str = "application/json"
) -> dict:
    try:
        return await resp.json(content_type=content_type)
    except ContentTypeError as e:
        bad_url = str(str(e).split(",")[2]).split("'")[1]
        raise FailedDecodeJson(f"Check args, URL is invalid\nURL- {bad_url}")


async def get_file_bytes(file: FileT) -> bytes:
    async with aiofiles.open(file, mode="rb") as f:
        return await f.read()


async def get_song(data: SongT) -> Union[AudioSegment]:

    if isinstance(data, (str, pathlib.Path)):
        song_bytes = await get_file_bytes(file=data)
        return AudioSegment.from_file(BytesIO(song_bytes))

    if isinstance(data, (bytes, bytearray)):
        return AudioSegment.from_file(BytesIO(data))

    if isinstance(data, AudioSegment):
        return data
