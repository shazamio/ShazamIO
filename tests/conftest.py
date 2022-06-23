import asyncio

import pytest_asyncio


@pytest_asyncio.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.run_until_complete(asyncio.sleep(1))
    loop.close()
