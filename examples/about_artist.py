import asyncio
from ShazamIO.api import Shazam
from ShazamIO.factory import ArtistInfo
from ShazamIO.misc import factory_artist


async def main():
    shazam = Shazam()
    artist_id = 43328183
    about_artist = await shazam.artist_about(artist_id)
    print(about_artist)

loop = asyncio.get_event_loop()
loop.run_until_complete(main())
