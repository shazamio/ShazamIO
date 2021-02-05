import aiohttp
from aiohttp import ContentTypeError
from ShazamIO.exceptions import FailedDecodeJson


async def validate_json(resp: aiohttp.ClientResponse, content_type: str = 'application/json') -> dict:
    try:
        return await resp.json(content_type=content_type)
    except ContentTypeError as e:
        bad_url = str(str(e).split(",")[2]).split("'")[1]
        raise FailedDecodeJson(f"Check args, URL is invalid\nURL- {bad_url}")
