import asyncio
from shazamio import Shazam
from shazamio import Serialize


async def main():
    shazam = Shazam()
    out = await shazam.recognize_song("data/dora.ogg")
    result = Serialize.full_track(data=out)
    youtube_data = await shazam.get_youtube_data(link=result.track.youtube_link)
    serialized_youtube = Serialize.youtube(data=youtube_data)
    print(serialized_youtube.uri)


loop = asyncio.get_event_loop_policy().get_event_loop()
loop.run_until_complete(main())
