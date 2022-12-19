import asyncio
from shazamio import Shazam, Serialize, GenreMusic


async def main():
    shazam = Shazam()
    top_rock_in_the_world = await shazam.top_world_genre_tracks(
        genre=GenreMusic.ROCK, limit=10
    )

    for track in top_rock_in_the_world["tracks"]:
        serialized_track = Serialize.track(data=track)
        print(serialized_track)


loop = asyncio.get_event_loop_policy().get_event_loop()
loop.run_until_complete(main())
