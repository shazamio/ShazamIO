import pathlib
from typing import Union

import aiofiles
import aiohttp
from aiohttp import ContentTypeError
from shazamio.exceptions import FailedDecodeJson

SongT = Union[str, pathlib.Path, bytes, bytearray]
FileT = Union[str, pathlib.Path]


async def validate_json(resp: aiohttp.ClientResponse, content_type: str = 'application/json') -> dict:
    try:
        return await resp.json(content_type=content_type)
    except ContentTypeError as e:
        bad_url = str(str(e).split(",")[2]).split("'")[1]
        raise FailedDecodeJson(f"Check args, URL is invalid\nURL- {bad_url}")


async def get_file_bytes(file: FileT) -> bytes:
    async with aiofiles.open(file, mode='rb') as f:
        return await f.read()


async def get_song_bytes(data: SongT) -> bytes:

    if isinstance(data, (str, pathlib.Path)):
        return await get_file_bytes(file=data)

    if isinstance(data, (bytes, bytearray)):
        return data

