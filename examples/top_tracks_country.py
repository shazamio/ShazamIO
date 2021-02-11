import asyncio
from ShazamIO.api import Shazam
from ShazamIO.factory import TrackInfo
from ShazamIO.misc import factory_track


async def main():
    shazam = Shazam()
    top_five_track_from_amsterdam = await shazam.top_country_tracks('NL', 5)
    for track in top_five_track_from_amsterdam['tracks']:
        serialized = factory_track.load(track, TrackInfo)
        print(serialized)

loop = asyncio.get_event_loop()
loop.run_until_complete(main())

