import asyncio
from shazamio import Shazam, Serialize


async def main():
    shazam = Shazam(language="EN")
    top_ten_moscow_tracks = await shazam.top_city_tracks(
        country_code="RU",
        city_name="Moscow",
        limit=10,
    )
    serialized = Serialize.playlists(top_ten_moscow_tracks)
    print(serialized)

    # for element in top_ten_moscow_tracks["data"]:
    #     serialized = Serialize.playlist(data=element)
    #     print(serialized)


loop = asyncio.get_event_loop_policy().get_event_loop()
loop.run_until_complete(main())
