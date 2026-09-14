import asyncio

from shazamio import GenreMusic, Shazam


async def main() -> None:
    shazam = Shazam()
    tracks = await shazam.top_country_genre_tracks(
        "ES",
        genre=GenreMusic.HIP_HOP_RAP,
        limit=4,
    )

    for track in tracks:
        print(f"{track.rank}. {track.artist} - {track.title}")


asyncio.run(main())
