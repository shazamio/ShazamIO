import asyncio
from ShazamIO.api import Shazam
from ShazamIO.factory import ArtistInfo
from ShazamIO.misc import factory_artist


async def main():
    shazam = Shazam()
    artists = await shazam.search_artist(query='Lil', limit=5)
    for artist in artists['artists']['hits']:
        serialized = factory_artist.load(artist, ArtistInfo)
        print(serialized)

loop = asyncio.get_event_loop()
loop.run_until_complete(main())
