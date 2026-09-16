import asyncio

from shazamio import Shazam


async def main() -> None:
    async with Shazam() as shazam:
        tracks = await shazam.top_country_tracks(
            country_code="NL",
            limit=5,
        )

        for track in tracks:
            print(f"{track.rank}. {track.artist} - {track.title}")


asyncio.run(main())
