import pytest

from shazamio import Shazam


@pytest.mark.asyncio
async def test_search_track():
    shazam = Shazam()
    result = await shazam.search_track(query="Lil", limit=5)
    assert "results" in result
    assert "songs" in result["results"]
    songs = result["results"]["songs"]["data"]
    assert len(songs) > 0
    for song in songs:
        assert "id" in song
        assert "attributes" in song
        assert "artistName" in song["attributes"]


@pytest.mark.asyncio
async def test_search_artist():
    shazam = Shazam()
    result = await shazam.search_artist(query="Lil", limit=5)
    assert "results" in result
    assert "artists" in result["results"]
    artists = result["results"]["artists"]["data"]
    assert len(artists) > 0
    for artist in artists:
        assert "id" in artist
        assert "attributes" in artist
        assert "name" in artist["attributes"]
