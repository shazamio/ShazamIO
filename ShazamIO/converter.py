from ShazamIO.typehints import *
from ShazamIO.models import *
import aiohttp


class Converter(Request):

    @staticmethod
    def data_search(timezone: str, uri: str, samplems: int, timestamp: int) -> dict:
        return {'timezone': timezone, 'signature': {'uri': uri, 'samplems': samplems},
                'timestamp': timestamp, 'context': {}, 'geolocation': {}}

    @staticmethod
    async def city_id_from(city: CityName) -> CityID:
        async with aiohttp.ClientSession() as session:
            async with session.get(ShazamUrl.CITY_ID) as resp:
                data = await resp.json()
                for k, v in data.items():
                    if v == city:
                        return k.split('_')[2]

