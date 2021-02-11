import asyncio
from ShazamIO.api import Shazam
from ShazamIO.factory import TrackInfo
from ShazamIO.misc import factory_track


async def main():
    shazam = Shazam()
    artist_id = 201896832
    top_three_artist_tracks = await shazam.artist_top_tracks(artist_id=artist_id, limit=3)  # JSON
    for track in top_three_artist_tracks['tracks']:
        serialized_track = factory_track.load(track, TrackInfo)
        print(serialized_track)

loop = asyncio.get_event_loop()
loop.run_until_complete(main())
