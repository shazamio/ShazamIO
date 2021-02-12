import asyncio
from ShazamIO.api import Shazam
from ShazamIO.converter import Geo
from ShazamIO.factory import TrackInfo
from ShazamIO.misc import factory_track


async def main():
    shazam = Shazam()
    moscow_id = await Geo().city_id_from('RU', 'Moscow')
    top_ten_moscow_tracks = await shazam.top_city_tracks(city_id=moscow_id, limit=10)
    print(top_ten_moscow_tracks)
    for track in top_ten_moscow_tracks['tracks']:
        serialized = factory_track.load(track, TrackInfo)
        print(serialized)

loop = asyncio.get_event_loop()
loop.run_until_complete(main())

