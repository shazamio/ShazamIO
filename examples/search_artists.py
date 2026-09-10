import asyncio

from shazamio import Serialize, Shazam


async def main() -> None:
    shazam = Shazam()
    artists = await shazam.search_artist(query="LIL", limit=5)
    for artist in artists["artists"]["hits"]:
        serialized = Serialize.artist(data=artist)
        print(serialized)
        print(artist)


loop = asyncio.get_event_loop_policy().get_event_loop()
loop.run_until_complete(main())
