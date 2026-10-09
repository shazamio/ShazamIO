import re
from collections.abc import AsyncGenerator
from http import HTTPStatus
from typing import Any, Final

import pytest
from vcr import VCR
from vcr.request import Request

from shazamio import Shazam

# The recognize path carries two fresh `uuid4` per request, so the recorded one
#  never equals the replayed one and `vcrpy`'s own `path` matcher finds nothing.
_UUID: Final[re.Pattern[str]] = re.compile(r"[0-9A-F]{8}(?:-[0-9A-F]{4}){3}-[0-9A-F]{12}")

_HEADERS_READ: Final[frozenset[str]] = frozenset({"content-type", "location"})


def _path_without_uuids(recorded: Request, replayed: Request, /) -> None:
    expected = _UUID.sub("<uuid>", recorded.path)
    actual = _UUID.sub("<uuid>", replayed.path)
    if expected != actual:
        msg = f"{expected} != {actual}"
        raise AssertionError(msg)


# `pluggy` passes a hook only the arguments it names, so `config` is left out.
def pytest_recording_configure(vcr: VCR) -> None:
    vcr.register_matcher("path_without_uuids", _path_without_uuids)


# Nothing matches on request headers, and a cassette is committed: whatever a
#  request carries (a proxy credential, a header added later) stays out of it.
def _as_recorded(request: Request) -> Request:
    request.headers = {}
    return request


def _as_replayed(response: dict[str, Any]) -> dict[str, Any] | None:
    # A `429` is retried by the client with backoff, so a recorded one makes the
    #  replay sleep through it again: seven of them made one test take 25s.
    #  Returning `None` leaves the response out of the cassette.
    #  https://github.com/kevin1024/vcrpy/blob/c599974b31f3e510df9b98e61513fe6889a50db0/vcr/cassette.py#L235-L237
    if response["status"]["code"] == HTTPStatus.TOO_MANY_REQUESTS:
        return None

    # The CDN headers name the edge nearest to whoever recorded, and nothing reads
    #  them: the client checks `Content-Type`, one test follows `Location`.
    response["headers"] = {
        name: values
        for name, values in response["headers"].items()
        if name.casefold() in _HEADERS_READ
    }

    # The library reads no HTML body, only the status and headers of the pages
    #  that answer with one, and each such body is the site's 450KB shell.
    content_types: list[str] = response["headers"].get("Content-Type", [])
    if any(content_type.startswith("text/html") for content_type in content_types):
        response["body"]["string"] = ""
    return response


@pytest.fixture(scope="module")
def vcr_config() -> dict[str, Any]:
    return {
        "match_on": ["method", "scheme", "host", "port", "path_without_uuids", "query"],
        "before_record_request": _as_recorded,
        "before_record_response": _as_replayed,
    }


# One client per test, closed with it. Without this every test that builds a
#  `Shazam` leaves its session open, and `aiohttp` reports each one at
#  collection: `Unclosed client session`.
@pytest.fixture
async def shazam() -> AsyncGenerator[Shazam, None]:
    async with Shazam() as client:
        yield client
