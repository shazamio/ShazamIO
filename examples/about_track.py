import asyncio

from shazamio import Shazam


async def main() -> None:
    async with Shazam() as shazam:
        track_id: int = 53982678
        track = await shazam.track_about(track_id=track_id)

        print(track.title, track.subtitle)


asyncio.run(main())
