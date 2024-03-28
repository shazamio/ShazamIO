import asyncio
from shazamio import Shazam, Serialize


async def main():
    shazam = Shazam()
    artist_id = 1300793014
    albums = await shazam.artist_albums(artist_id=artist_id)
    serialized = Serialize.artist_albums(data=albums)
    for i in serialized.data:
        print(f"{i.id} | {i.attributes.artist_name} ->>>>>>>> {i.attributes.name} - {i.attributes.track_count} {i.attributes.release_date}")


loop = asyncio.get_event_loop_policy().get_event_loop()
loop.run_until_complete(main())
