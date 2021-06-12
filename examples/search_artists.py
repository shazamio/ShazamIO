import asyncio
from shazamio import Shazam, serialize_artist


async def main():
    shazam = Shazam()
    artists = await shazam.search_artist(query='Lil', limit=5)
    for artist in artists['artists']['hits']:
        serialized = serialize_artist(data=artist)
        print(serialized)

loop = asyncio.get_event_loop()
loop.run_until_complete(main())
