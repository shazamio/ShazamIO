import pytest

from shazamio import Serialize
from shazamio import Shazam
from shazamio.schemas.artists import ArtistQuery
from shazamio.schemas.enums import ArtistExtend
from shazamio.schemas.enums import ArtistView


@pytest.mark.asyncio
async def test_about_artist():
    shazam = Shazam(language="ES")
    artist_id = 659860538

    about_artist = await shazam.artist_about(
        artist_id,
        query=ArtistQuery(
            views=[
                ArtistView.FULL_ALBUMS,
                ArtistView.LATEST_RELEASE,
            ],
            extend=[
                ArtistExtend.ARTIST_BIO,
                ArtistExtend.BORN_OF_FORMED,
                ArtistExtend.EDITORIAL_ARTWORK,
                ArtistExtend.ORIGIN,
            ],
        ),
    )

    serialized = Serialize.artist_v2(about_artist)
    assert serialized.data[0].attributes.name == "Markul"
    assert "Hip-hop/Rap" in serialized.data[0].attributes.genre_names
