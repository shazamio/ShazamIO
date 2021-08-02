import asyncio
from shazamio import Shazam, serialize_track


async def main():
    shazam = Shazam()
    artist_id = 201896832
    top_three_artist_tracks = await shazam.artist_top_tracks(artist_id=artist_id, limit=3)
    for track in top_three_artist_tracks['tracks']:
        serialized_track = serialize_track(data=track)
        print(serialized_track)

loop = asyncio.get_event_loop()
loop.run_until_complete(main())
