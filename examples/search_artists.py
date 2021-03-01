import asyncio
from shazamio import Shazam, FactoryArtist


async def main():
    shazam = Shazam()
    artists = await shazam.search_artist(query='Lil', limit=5)
    for artist in artists['artists']['hits']:
        serialized = FactoryArtist(artist).serializer()
        print(serialized)

loop = asyncio.get_event_loop()
loop.run_until_complete(main())
