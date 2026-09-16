import asyncio

from shazamio import Shazam


async def main() -> None:
    async with Shazam() as shazam:
        track_id: int = 546891609
        related = await shazam.related_tracks(
            track_id=track_id,
            limit=5,
            offset=2,
        )
        # ONLY №3, №4 SONG
        print(related)


asyncio.run(main())
