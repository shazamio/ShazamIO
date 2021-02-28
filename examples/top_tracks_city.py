import asyncio
from ShazamIO import Shazam, FactoryTrack, Geo


async def main():
    shazam = Shazam()
    moscow_id = await Geo(country='RU', city='Moscow').city_id_from()
    top_ten_moscow_tracks = await shazam.top_city_tracks(city_id=moscow_id, limit=10)
    print(top_ten_moscow_tracks)
    # ALL TRACKS DICT
    for track in top_ten_moscow_tracks['tracks']:
        serialized = FactoryTrack(track)
        # SERIALIZE FROM DATACLASS FACTORY
        print(serialized)

loop = asyncio.get_event_loop()
loop.run_until_complete(main())

