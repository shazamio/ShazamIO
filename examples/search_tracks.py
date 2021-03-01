import asyncio
from shazamio import Shazam


async def main():
    shazam = Shazam()
    tracks = await shazam.search_track(query='Lil', limit=5)
    print(tracks)

loop = asyncio.get_event_loop()
loop.run_until_complete(main())
