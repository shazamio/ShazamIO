import asyncio
from shazamio import Shazam, Serialize

async def main():
    proxy = 'http://your_user:your_password@your_proxy_url:your_proxy_port'
    shazam = Shazam(proxy=proxy) #All requests will be made with this proxy
    out = await shazam.recognize_song("data/dora.ogg")
    print(out)

    serialized = Serialize.full_track(out)
    print(serialized)


loop = asyncio.get_event_loop_policy().get_event_loop()
loop.run_until_complete(main())
