import aiohttp

from ShazamIO.utils import validate_json


class HTTPClient:

    @staticmethod
    async def request(method: str, url: str, *args, **kwargs) -> aiohttp.ClientResponse:
        async with aiohttp.ClientSession() as session:
            if method.upper() == 'GET':
                async with session.get(url, **kwargs) as resp:
                    return await validate_json(resp, *args)
            elif method.upper() == 'POST':
                async with session.post(url, **kwargs) as resp:
                    return await validate_json(resp, *args)
            else:
                raise Exception('Wrong method (Accept: GET/POST')
