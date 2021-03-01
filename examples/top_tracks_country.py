import asyncio
from shazamio import Shazam, FactoryTrack


async def main():
    shazam = Shazam()
    top_five_track_from_amsterdam = await shazam.top_country_tracks('NL', 5)
    for track in top_five_track_from_amsterdam['tracks']:
        serialized = FactoryTrack(data=track).serializer()
        print(serialized)

loop = asyncio.get_event_loop()
loop.run_until_complete(main())

