import socket
from collections.abc import AsyncGenerator
from typing import NoReturn

import pytest

from shazamio import Shazam


def pytest_addoption(parser: pytest.Parser) -> None:
    parser.addoption(
        "--live",
        action="store_true",
        help="Also run the tests marked `live`, which call the real Shazam and Apple services.",
    )


# A test not marked `live` may resolve no host name at all, so one that quietly
#  calls a real service fails at once instead of flaking whenever Shazam moves. Without
#  `aiodns` installed, `aiohttp` resolves through the loop's executor, which looks
#  up `socket.getaddrinfo` at every call, so replacing it is enough.
#  https://github.com/aio-libs/aiohttp/blob/5e392ce0456f5235a4ee6ad46f0e806df2f15873/aiohttp/resolver.py#L301
#  https://github.com/python/cpython/blob/ebf955df7a89ed0c7968f79faec1de49f61ed7cb/Lib/asyncio/base_events.py#L934
@pytest.fixture(autouse=True)
def _network_only_when_live(
    request: pytest.FixtureRequest,
    *,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    if request.node.get_closest_marker("live") is not None:
        if not request.config.getoption("--live"):
            pytest.skip("calls the real service; run `just test-live`")
        return

    node_id: str = request.node.nodeid

    # Called positionally by the loop's executor, so the signature is positional too.
    def refuse(host: bytes | str | None, port: bytes | str | int | None, /, *_: int) -> NoReturn:
        msg = f"{node_id} resolved {host!r}:{port}; mark it `@pytest.mark.live`"
        raise OSError(msg)

    monkeypatch.setattr(socket, "getaddrinfo", refuse)


# One client per test, closed with it. Without this every test that builds a
#  `Shazam` leaves its session open, and `aiohttp` reports each one at
#  collection: `Unclosed client session`.
@pytest.fixture
async def shazam() -> AsyncGenerator[Shazam, None]:
    async with Shazam() as client:
        yield client
