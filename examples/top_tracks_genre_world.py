import asyncio
from shazamio import Shazam, serialize_track, GenreMusic


async def main():
    shazam = Shazam()
    top_rock_in_the_world = await shazam.top_world_genre_tracks(genre=GenreMusic.ROCK, limit=10)

    for track in top_rock_in_the_world['tracks']:
        serialized_track = serialize_track(data=track)
        print(serialized_track.spotify_url)


loop = asyncio.get_event_loop()
loop.run_until_complete(main())
