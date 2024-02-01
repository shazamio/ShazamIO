import aiohttp
import backoff

from shazamio.exceptions import BadMethod, TooManyRequests
from shazamio.utils import validate_json


class HTTPClient:
    @staticmethod
    @backoff.on_exception(backoff.expo, TooManyRequests)
    async def request(method: str, url: str, *args, **kwargs) -> dict:
        async with aiohttp.ClientSession() as session:
            if method.upper() == "GET":
                async with session.get(url, **kwargs) as resp:
                    return await validate_json(resp, *args)
            elif method.upper() == "POST":
                async with session.post(url, **kwargs) as resp:
                    if resp.status == 429:
                        raise TooManyRequests
                    return await validate_json(resp, *args)
            else:
                raise BadMethod("Accept only GET/POST")
