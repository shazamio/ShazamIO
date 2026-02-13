import pytest

from shazamio import Shazam


@pytest.mark.asyncio
async def test_related_tracks():
    shazam = Shazam()
    result = await shazam.related_tracks(track_id=546891609, limit=5)
    assert "tracks" in result
    assert len(result["tracks"]) > 0
