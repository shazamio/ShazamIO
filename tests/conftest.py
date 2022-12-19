import asyncio

import pytest_asyncio


@pytest_asyncio.fixture(scope="session", autouse=True)
def event_loop():
    loop = asyncio.get_event_loop_policy().get_event_loop()
    yield loop
    loop.run_until_complete(asyncio.sleep(0.025))
    loop.close()
