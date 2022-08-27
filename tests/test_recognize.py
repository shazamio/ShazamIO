import pytest_asyncio
from pydub import AudioSegment
from io import BytesIO

from shazamio import Shazam
from shazamio.utils import get_file_bytes



@pytest_asyncio.fixture(scope="session")
async def song_bytes():
    yield await get_file_bytes(file="examples/data/dora.ogg")


async def test_recognize_song_file():
    shazam = Shazam()
    out = await shazam.recognize_song(data="examples/data/dora.ogg")

    assert out.get("matches") != []
    assert out["track"]["key"] == "549679333"


async def test_recognize_song_bytes(song_bytes: bytes):
    shazam = Shazam()
    out = await shazam.recognize_song(data=song_bytes)

    assert out.get("matches") != []
    assert out["track"]["key"] == "549679333"


async def test_recognize_song_too_short():
    short_audio_segment = AudioSegment.from_file(file=BytesIO(b'0'*126),
                                                 format='pcm',
                                                 sample_width=2,
                                                 frame_rate=16000,
                                                 channels=1)

    shazam = Shazam()
    out = await shazam.recognize_song(data=short_audio_segment)

    assert out.get("matches") == []
    assert "track" not in out