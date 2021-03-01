import asyncio
from shazamio import Shazam, FactoryTrack


async def main():
    shazam = Shazam()
    track_id = 552406075
    about_track = await shazam.track_about(track_id=track_id)
    serialized = FactoryTrack(data=about_track).serializer()

    print(about_track)  # dict
    print(serialized)  # serialized from dataclass factory

loop = asyncio.get_event_loop()
loop.run_until_complete(main())
