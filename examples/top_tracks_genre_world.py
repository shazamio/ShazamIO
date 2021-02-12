import asyncio
from ShazamIO.api import Shazam
from ShazamIO.factory import TrackInfo
from ShazamIO.misc import factory_track


async def main():
    shazam = Shazam()
    top_rock_in_the_world = await shazam.top_world_genre_tracks(genre=7, limit=10)
    print(top_rock_in_the_world)

    for track in top_rock_in_the_world['tracks']:
        serialized_track = factory_track.load(track, TrackInfo)
        print(serialized_track.spotify_url)


loop = asyncio.get_event_loop()
loop.run_until_complete(main())
