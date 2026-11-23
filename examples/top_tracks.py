import asyncio

from shazamio import GenreMusic, Shazam


async def main() -> None:
    async with Shazam() as shazam:
        world = await shazam.top_tracks()
        world_rock = await shazam.top_tracks(genre=GenreMusic.ROCK)
        netherlands = await shazam.top_tracks("NL")
        spain_hip_hop = await shazam.top_tracks("ES", genre=GenreMusic.HIP_HOP_RAP)
        moscow = await shazam.top_tracks("RU", city="Moscow")

        for chart in (world, world_rock, netherlands, spain_hip_hop, moscow):
            for track in chart[:3]:
                print(f"{track.rank}. {track.artist} - {track.title}")


asyncio.run(main())
