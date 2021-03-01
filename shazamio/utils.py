import aiofiles
import aiohttp
from aiohttp import ContentTypeError
from shazamio.exceptions import FailedDecodeJson


async def validate_json(resp: aiohttp.ClientResponse, content_type: str = 'application/json') -> dict:
    try:
        return await resp.json(content_type=content_type)
    except ContentTypeError as e:
        bad_url = str(str(e).split(",")[2]).split("'")[1]
        raise FailedDecodeJson(f"Check args, URL is invalid\nURL- {bad_url}")


async def load_file(file, binary=False):
    mode = "r" if not binary else "rb"
    async with aiofiles.open(file, mode=mode) as f:
        return await f.read()


