import aiohttp

from shazamio.exceptions import BadMethod
from shazamio.utils import validate_json


class HTTPClient:
    def __init__(self, *args, **kwargs):
        self.http_session = aiohttp.ClientSession()

    async def stop(self):
        await self.http_session.close()

    async def request(self, method: str, url: str, *args, **kwargs) -> dict:
        if method.upper() == "GET":
            async with self.http_session.get(url, **kwargs) as resp:
                return await validate_json(resp, *args)
        elif method.upper() == "POST":
            async with self.http_session.post(url, **kwargs) as resp:
                return await validate_json(resp, *args)
        else:
            raise BadMethod("Accept only GET/POST")
