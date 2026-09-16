from collections.abc import AsyncIterator

import pytest

from shazamio import Shazam


# One client per test, closed with it. Without this every test that builds a
#  `Shazam` leaves its session open, and `aiohttp` reports each one at
#  collection: `Unclosed client session`.
@pytest.fixture
async def shazam() -> AsyncIterator[Shazam]:
    async with Shazam() as client:
        yield client
