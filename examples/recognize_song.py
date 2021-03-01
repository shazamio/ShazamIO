import asyncio
from shazamio import Shazam


async def main():
    shazam = Shazam()
    out = await shazam.recognize_song('data/dora.ogg')
    print(out)

loop = asyncio.get_event_loop()
loop.run_until_complete(main())
