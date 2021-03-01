import asyncio
from ShazamIO import Shazam, GenreMusic


async def main():
    shazam = Shazam()
    top_spain_rap = await shazam.top_country_genre_tracks(country='ES',
                                                          genre=GenreMusic.HIP_HOP_RAP,
                                                          limit=4)
    print(top_spain_rap)

loop = asyncio.get_event_loop()
loop.run_until_complete(main())
