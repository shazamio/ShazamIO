import asyncio
from functools import wraps, partial

import aiofiles
import aiohttp
from aiohttp import ContentTypeError
from ShazamIO.exceptions import FailedDecodeJson


async def validate_json(resp: aiohttp.ClientResponse, content_type: str = 'application/json') -> dict:
    try:
        return await resp.json(content_type=content_type)
    except ContentTypeError as e:
        bad_url = str(str(e).split(",")[2]).split("'")[1]
        raise FailedDecodeJson(f"Check args, URL is invalid\nURL- {bad_url}")


def threaded(func):
    @wraps(func)
    async def wrap(*args, **kwargs):
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, partial(func, *args, **kwargs))
    return wrap


async def load_file(file, binary=False):
    mode = "r" if not binary else "rb"
    async with aiofiles.open(file, mode=mode) as f:
        return await f.read()


