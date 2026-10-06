import asyncio

from shazamio import Serialize, Shazam


async def main() -> None:
    async with Shazam() as shazam:
        tracks = await shazam.search_tracks_via_itunes("daft punk one more time")

        for about_track in tracks:
            track = Serialize.track(data=about_track)
            print(track.key, track.subtitle, track.title)


asyncio.run(main())
