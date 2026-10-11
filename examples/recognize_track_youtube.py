import asyncio

from shazamio import Serialize, Shazam


async def main() -> None:
    async with Shazam() as shazam:
        out = await shazam.recognize("data/Gloria.ogg")
        track = Serialize.full_track(out).track

        youtube_data = await shazam.get_youtube_data(link=track.youtube_link)
        print(Serialize.youtube(youtube_data).uri)  # https://youtu.be/6dYWe1c3OyU?autoplay=1


asyncio.run(main())
