import asyncio
from shazamio import Shazam, serialize_track


async def main():
    shazam = Shazam()
    track_id = 552406075
    about_track = await shazam.track_about(track_id=track_id)
    serialized = serialize_track(data=about_track)

    print(about_track)  # dict
    print(serialized)  # serialized from dataclass factory

loop = asyncio.get_event_loop()
loop.run_until_complete(main())
