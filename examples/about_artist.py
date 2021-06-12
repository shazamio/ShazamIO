import asyncio
from shazamio import Shazam, serialize_artist


async def main():
    shazam = Shazam()
    artist_id = 43328183
    about_artist = await shazam.artist_about(artist_id)
    serialized = serialize_artist(about_artist)

    print(about_artist)  # dict
    print(serialized)  # serialized from dataclass factory

loop = asyncio.get_event_loop()
loop.run_until_complete(main())
