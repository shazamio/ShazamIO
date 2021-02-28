import asyncio
from ShazamIO import Shazam


async def main():
    shazam = Shazam()
    top_spain_rap = await shazam.top_country_genre_tracks(country='ES', genre=2, limit=4)
    print(top_spain_rap)

loop = asyncio.get_event_loop()
loop.run_until_complete(main())

