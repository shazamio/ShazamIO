import asyncio
from pprint import pprint

from shazamio import Shazam, Serialize
from shazamio.schemas.artists import ArtistQuery
from shazamio.schemas.enums import ArtistView


async def main():
    shazam = Shazam()
    artist_id = 1081606072

    about_artist = await shazam.artist_about(
        artist_id,
        query=ArtistQuery(
            views=[
                ArtistView.TOP_SONGS,
            ],
        ),
    )
    serialized = Serialize.artist_v2(about_artist)
    for i in serialized.data[0].views.top_songs.data:
        pprint(i.attributes.name)


loop = asyncio.get_event_loop_policy().get_event_loop()
loop.run_until_complete(main())
