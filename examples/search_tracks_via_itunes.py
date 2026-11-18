import asyncio

from shazamio import Shazam


async def main() -> None:
    async with Shazam() as shazam:
        tracks = await shazam.search_tracks_via_itunes("daft punk one more time")

        for track in tracks:
            print(track.key, track.subtitle, track.title)


asyncio.run(main())
