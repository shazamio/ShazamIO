import pytest

from shazamio import Shazam, GenreMusic


@pytest.mark.asyncio
async def test_top_world_tracks():
    shazam = Shazam()
    result = await shazam.top_world_tracks(limit=5)
    assert "tracks" in result
    tracks = result["tracks"]
    assert len(tracks) == 5
    for track in tracks:
        assert "rank" in track
        assert "title" in track
        assert "subtitle" in track


@pytest.mark.asyncio
async def test_top_country_tracks():
    shazam = Shazam()
    result = await shazam.top_country_tracks(country_code="ES", limit=4)
    assert "tracks" in result
    tracks = result["tracks"]
    assert len(tracks) == 4
    for track in tracks:
        assert "rank" in track
        assert "title" in track
        assert "subtitle" in track


@pytest.mark.asyncio
async def test_top_city_tracks():
    shazam = Shazam()
    result = await shazam.top_city_tracks(
        country_code="RU",
        city_name="Moscow",
        limit=5,
    )
    assert "tracks" in result
    tracks = result["tracks"]
    assert len(tracks) == 5


@pytest.mark.asyncio
async def test_top_world_genre_tracks():
    shazam = Shazam()
    result = await shazam.top_world_genre_tracks(
        genre=GenreMusic.ROCK,
        limit=10,
    )
    assert "tracks" in result
    tracks = result["tracks"]
    assert len(tracks) == 10


@pytest.mark.asyncio
async def test_top_country_genre_tracks():
    shazam = Shazam()
    result = await shazam.top_country_genre_tracks(
        country_code="ES",
        genre=GenreMusic.HIP_HOP_RAP,
        limit=4,
    )
    assert "tracks" in result
    tracks = result["tracks"]
    assert len(tracks) == 4
