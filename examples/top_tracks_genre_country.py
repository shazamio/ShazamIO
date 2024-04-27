import asyncio
from shazamio import Shazam, GenreMusic, Serialize


async def main():
    shazam = Shazam()
    top_spain_rap = await shazam.top_country_genre_tracks(
        country_code="ES",
        genre=GenreMusic.HIP_HOP_RAP,
        limit=4,
    )
    serialized = Serialize.playlists(top_spain_rap)
    print(serialized)

    for playlist in top_spain_rap["data"]:
        serialized = Serialize.playlist(data=playlist)
        print(serialized)


loop = asyncio.get_event_loop_policy().get_event_loop()
loop.run_until_complete(main())
