import asyncio
from shazamio import Shazam, Serialize


async def main():
    shazam = Shazam()
    top_five_track_from_amsterdam = await shazam.top_country_tracks("NL", 5)
    for track in top_five_track_from_amsterdam["tracks"]:
        serialized = Serialize.track(data=track)
        print(serialized)


loop = asyncio.get_event_loop()
loop.run_until_complete(main())
