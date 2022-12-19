import asyncio
from pprint import pprint

from shazamio import Shazam, Serialize
from shazamio.schemas.artists import ArtistQuery
from shazamio.schemas.enums import ArtistExtend
from shazamio.schemas.enums import ArtistView


async def main():
    shazam = Shazam(language="ES")
    artist_id = 1124753799
    # extend: artistBio,bornOrFormed,editorialArtwork,origin
    # views: full-albums,featured-albums,latest-release,top-music-videos,similar-artists,
    # top-songs,playlists

    about_artist = await shazam.artist_about(
        artist_id,
        query=ArtistQuery(
            views=[
                ArtistView.FULL_ALBUMS,
                ArtistView.FEATURED_ALBUMS,
                ArtistView.LATEST_RELEASE,
                ArtistView.TOP_MUSIC_VIDEOS,
                ArtistView.SIMULAR_ARTISTS,
            ],
            extend=[
                ArtistExtend.ARTIST_BIO,
                ArtistExtend.BORN_OF_FORMED,
                ArtistExtend.EDITORIAL_ARTWORK,
                ArtistExtend.ORIGIN,
            ],
        ),
    )
    print(about_artist)  # dict
    serialized = Serialize.artist_v2(about_artist)
    pprint(serialized)  # serialized from pydantic


loop = asyncio.get_event_loop_policy().get_event_loop()
loop.run_until_complete(main())
