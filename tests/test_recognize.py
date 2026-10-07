import warnings
from pathlib import Path

import pytest
from shazamio_core import SignatureError

from shazamio import SearchParams, Shazam


@pytest.fixture(scope="session")
def song_bytes() -> bytes:
    return Path("examples/data/Gloria.ogg").read_bytes()


@pytest.mark.asyncio
async def test_recognize_file(shazam: Shazam) -> None:
    out = await shazam.recognize(data="examples/data/Gloria.ogg")
    assert out.get("matches") != []
    assert out["track"]["key"] == "53982678"


@pytest.mark.asyncio
async def test_recognize_bytes(song_bytes: bytes, shazam: Shazam) -> None:
    out = await shazam.recognize(data=song_bytes)
    assert out.get("matches") != []
    assert out["track"]["key"] == "53982678"


@pytest.mark.parametrize(
    ("seconds", "match"),
    [
        pytest.param(10, "clients send a 12 s window", id="old-default"),
        pytest.param(14, "clients send a 12 s window", id="below-no-match"),
        pytest.param(15, "returns no matches", id="no-match-floor"),
    ],
)
async def test_a_window_other_than_twelve_warns_at_the_caller(seconds: int, *, match: str) -> None:
    with pytest.warns(UserWarning, match=match) as record:
        shazam = Shazam(segment_duration_seconds=seconds)
    await shazam.close()

    assert record[0].filename == __file__


async def test_the_default_window_does_not_warn() -> None:
    with warnings.catch_warnings():
        warnings.simplefilter("error")
        shazam = Shazam()
    await shazam.close()


async def test_a_window_in_options_warns_at_the_caller(shazam: Shazam) -> None:
    # A missing file fails in the fingerprinting, after the check and before any request.
    with (
        pytest.warns(UserWarning, match="returns no matches") as record,
        pytest.raises(SignatureError),
    ):
        await shazam.recognize(
            "missing.ogg",
            options=SearchParams(segment_duration_seconds=16),
        )

    assert record[0].filename == __file__
