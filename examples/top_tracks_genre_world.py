import asyncio

from shazamio import GenreMusic, Shazam


async def main() -> None:
    async with Shazam() as shazam:
        tracks = await shazam.top_world_genre_tracks(
            genre=GenreMusic.ROCK,
            limit=10,
        )

        for track in tracks:
            print(f"{track.rank}. {track.artist} - {track.title}")


asyncio.run(main())
