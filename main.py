from ShazamIO.api import *
import asyncio


async def main():
    mp3_file_content_to_recognize = open('data/dora.ogg', 'rb').read()
    shazam = Shazam(mp3_file_content_to_recognize)
    recognize_generator = await shazam.recognize_song()
    print(recognize_generator)

loop = asyncio.get_event_loop()
loop.run_until_complete(main())
