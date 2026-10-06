import warnings
from collections.abc import AsyncIterator
from io import BytesIO

import pytest
import pytest_asyncio
from pydub import AudioSegment
from shazamio_core import SignatureError

from shazamio import SearchParams, Shazam
from shazamio.utils import get_file_bytes


@pytest_asyncio.fixture(scope="session")
async def song_bytes() -> AsyncIterator[bytes]:
    bytes_data = await get_file_bytes(file="examples/data/Gloria.ogg")
    yield bytes_data


@pytest.mark.asyncio
async def test_recognize_song_file(shazam: Shazam) -> None:
    out = await shazam.recognize(data="examples/data/Gloria.ogg")
    assert out.get("matches") != []
    assert out["track"]["key"] == "53982678"


@pytest.mark.asyncio
async def test_recognize_song_bytes(song_bytes: bytes, shazam: Shazam) -> None:
    out = await shazam.recognize(data=song_bytes)
    assert out.get("matches") != []
    assert out["track"]["key"] == "53982678"


@pytest.mark.asyncio
async def test_recognize_song_too_short(shazam: Shazam) -> None:
    short_audio_segment = AudioSegment.from_file(
        file=BytesIO(b"0" * 126),
        format="pcm",
        sample_width=2,
        frame_rate=16000,
        channels=1,
    )

    out = await shazam.recognize_song(data=short_audio_segment)

    assert out.get("matches") == []
    assert "track" not in out


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
