import asyncio
from ShazamIO.api import Shazam


async def main():
    shazam = Shazam()
    out = await shazam.recognize_song('dora.ogg')
    print(out)

loop = asyncio.get_event_loop()
loop.run_until_complete(main())
