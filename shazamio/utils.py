import pathlib
from enum import Enum
from io import BytesIO
from typing import Any, TypeAlias

import aiofiles
import aiohttp
from aiohttp import ContentTypeError
from pydub import AudioSegment

from shazamio.exceptions import FailedDecodeJson
from shazamio.schemas.artists import ArtistQuery

SongT: TypeAlias = str | pathlib.Path | bytes | bytearray
FileT: TypeAlias = str | pathlib.Path


async def validate_json(
    resp: aiohttp.ClientResponse,
    content_type: str = "application/json",
) -> Any:
    try:
        return await resp.json(content_type=content_type)
    except ContentTypeError as er:
        body = await resp.text()
        msg = f"Failed to decode json (status={resp.status}): {body[:200]}"
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


class QueryBuilder:
    def __init__(
        self,
        source: list[str | Enum],
    ) -> None:
        self.source = source

    def to_str(self) -> str:
        return ",".join(self.source)


class ArtistQueryGenerator:
    def __init__(
        self,
        source: ArtistQuery | None = None,
    ) -> None:
        self.source = source

    def params(self) -> dict[str, str]:
        return {
            "extend": QueryBuilder(source=self.source.extend or []).to_str(),
            "views": QueryBuilder(source=self.source.views or []).to_str(),
        }
