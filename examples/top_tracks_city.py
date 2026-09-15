import asyncio

from shazamio import Shazam


async def main() -> None:
    shazam = Shazam()
    tracks = await shazam.top_city_tracks(
        country_code="RU",
        city_name="Moscow",
        limit=10,
    )

    for track in tracks:
        print(f"{track.rank}. {track.artist} - {track.title}")


asyncio.run(main())
