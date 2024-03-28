import asyncio
from shazamio import Shazam, Serialize


async def main():
    shazam = Shazam()
    albums = await shazam.search_album(album_id=1544741796)
    serialized = Serialize.album_info(data=albums)

    for i in serialized.data[0].relationships.tracks.data:
        msg = f"{i.id} | {i.attributes.album_name} | {i.attributes.artist_name} [{i.attributes.name}]"
        print(msg)

loop = asyncio.get_event_loop_policy().get_event_loop()
loop.run_until_complete(main())
