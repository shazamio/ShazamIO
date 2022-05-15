import asyncio
from functools import wraps

import pytest

try:
    from asyncio.proactor_events import _ProactorBasePipeTransport

    HAS_PROACTOR = True
except ImportError:
    _ProactorBasePipeTransport = None
    HAS_PROACTOR = False


@pytest.fixture(scope="module")
def silence_event_loop_closed():
    """
    Mostly used to suppress "unhandled exception" error due to
    ``_ProactorBasePipeTransport`` raising an exception when doing ``__del__``
    """
    if not HAS_PROACTOR:
        return False
    assert _ProactorBasePipeTransport is not None
    if hasattr(_ProactorBasePipeTransport, "old_del"):
        return True

    # From: https://github.com/aio-libs/aiohttp/issues/4324#issuecomment-733884349
    def silencer(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            try:
                return func(self, *args, **kwargs)
            except RuntimeError as e:
                if str(e) != "Event loop is closed":
                    raise

        return wrapper

    # noinspection PyUnresolvedReferences
    old_del = _ProactorBasePipeTransport.__del__
    _ProactorBasePipeTransport._old_del = old_del
    _ProactorBasePipeTransport.__del__ = silencer(old_del)
    return True


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop()
    yield loop
    loop.run_until_complete(asyncio.sleep(1))
    loop.close()
