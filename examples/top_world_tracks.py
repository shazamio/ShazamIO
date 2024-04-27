import asyncio
from shazamio import Shazam, Serialize


async def main():
    shazam = Shazam()
    top_world_tracks = await shazam.top_world_tracks(limit=10)
    serialized = Serialize.playlists(top_world_tracks)
    print(serialized)

    for playlist in top_world_tracks["data"]:
        serialized = Serialize.playlist(data=playlist)
        print(serialized)


loop = asyncio.get_event_loop_policy().get_event_loop()
loop.run_until_complete(main())
