import asyncio
from shazamio import Shazam, serialize_track


async def main():
    shazam = Shazam()
    top_world_tracks = await shazam.top_world_tracks(limit=10)
    print(top_world_tracks)
    for track in top_world_tracks['tracks']:
        serialized = serialize_track(track)
        print(serialized)

loop = asyncio.get_event_loop()
loop.run_until_complete(main())
