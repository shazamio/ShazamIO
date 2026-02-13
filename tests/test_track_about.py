import pytest

from shazamio import Shazam


@pytest.mark.asyncio
async def test_track_about():
    shazam = Shazam()
    result = await shazam.track_about(track_id=552406075)
    assert result["title"] == "Ale jazz!"
    assert "key" in result
