import asyncio

import aiohttp
import pytest

from shazamio import Serialize
from shazamio import Shazam


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop()

    yield loop

    pending = asyncio.tasks.all_tasks(loop)
    loop.run_until_complete(asyncio.gather(*pending))
    loop.run_until_complete(asyncio.sleep(1))

    loop.close()


@pytest.fixture(scope="session")
async def song_bytes_instagram():
    URL = "https://scontent.cdninstagram.com/v/t50.2886-16" \
          "/279321904_309072168068152_5426544396712203425_n.mp4?_nc_ht=scontent-lga3-1" \
          ".cdninstagram.com&_nc_cat=104&_nc_ohc=2s71AQMoTOYAX8rhF1Q&edm=AABBvjUBAAAA&ccb=7-4&oh" \
          "=00_AT9dYyXY3fkCk2LS3nzkm7krqzB7f3LS9LtgSO27r1tACA&oe=6283ABB2&_nc_sid=83d603" \
          "&bytestart=23521&byteend=14360"
    async with aiohttp.ClientSession() as session:
        async with session.request(method='GET', url=URL) as resp:
            yield await resp.read()


@pytest.fixture(scope="session")
async def song_bytes_twitter():
    URL = "https://video.twimg.com/ext_tw_video/1522975571994632197/pu/vid/720x720" \
          "/9FB7F8B1KZ1WHCXJ.mp4?tag=12"
    async with aiohttp.ClientSession() as session:
        async with session.request(method='GET', url=URL) as resp:
            yield await resp.read()


@pytest.mark.asyncio(scope="session")
async def test_recognize_song_twitter(song_bytes_twitter: bytes):
    shazam = Shazam()
    out = await shazam.recognize_song(data=song_bytes_twitter)
    serialize_out = Serialize.full_track(data=out)
    assert serialize_out.matches[0].channel is None


@pytest.mark.asyncio(scope="session")
async def test_recognize_song_instagram(song_bytes_instagram: bytes):
    shazam = Shazam()
    out = await shazam.recognize_song(data=song_bytes_instagram)
    serialize_out = Serialize.full_track(data=out)
    assert serialize_out.matches[0].channel is None
