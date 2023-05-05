import asyncio
from shazamio import Shazam, Serialize


async def main():
    shazam = Shazam(language="GB")
    top_ten_moscow_tracks = await shazam.top_city_tracks(
        country_code="RU",
        city_name="Moscow",
        limit=10,
    )
    print(top_ten_moscow_tracks)
    # ALL TRACKS DICT
    for track in top_ten_moscow_tracks["tracks"]:
        serialized = Serialize.track(data=track)
        # SERIALIZE FROM DATACLASS FACTORY
        print(serialized)


loop = asyncio.get_event_loop_policy().get_event_loop()
loop.run_until_complete(main())
