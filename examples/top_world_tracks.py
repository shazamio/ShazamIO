import asyncio

from shazamio import Shazam


async def main() -> None:
    shazam = Shazam()
    tracks = await shazam.top_world_tracks(limit=10)

    for track in tracks:
        print(f"{track.rank}. {track.artist} - {track.title}")


asyncio.run(main())
