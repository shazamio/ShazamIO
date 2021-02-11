import asyncio
from ShazamIO.api import Shazam
from ShazamIO.factory import TrackInfo
from ShazamIO.misc import factory_track


async def main():
    shazam = Shazam()
    top_world_tracks = await shazam.top_world_tracks(limit=10)  # API JSON
    for track in top_world_tracks['tracks']:
        serialized = factory_track.load(track, TrackInfo)
        print(serialized)

loop = asyncio.get_event_loop()
loop.run_until_complete(main())
