import asyncio
from ShazamIO.api import Shazam
from ShazamIO.factory import TrackInfo
from ShazamIO.misc import factory_track


async def main():
    shazam = Shazam()
    track_id = 552406075
    about_track = await shazam.track_about(track_id=track_id)
    serialized = factory_track.load(about_track, TrackInfo)
    print(serialized)

loop = asyncio.get_event_loop()
loop.run_until_complete(main())
