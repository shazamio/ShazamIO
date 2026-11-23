from dataclasses import dataclass
from http import HTTPMethod, HTTPStatus
from typing import ClassVar, Final

import pytest

from shazamio import BadResponse, Endpoint, Request, Response, Settings, Shazam
from shazamio.testing import MockTransport

_TEXT: Final[str] = "text/plain"


@dataclass(frozen=True, kw_only=True)
class _Greeting(Endpoint[str]):
    content_type: ClassVar[str] = _TEXT

    name: str

    def request(self, settings: Settings) -> Request:
        return Request(
            method=HTTPMethod.GET,
            url=f"https://greeting.example.com/{settings.language}/{settings.country}",
            params={"name": self.name},
        )

    def parse(self, payload: str) -> str:
        return payload.upper()


def _answer(content_type: str) -> MockTransport:
    return MockTransport(
        lambda _request: Response(
            status=HTTPStatus.OK,
            content_type=content_type,
            text="hello",
        ),
    )


@pytest.mark.asyncio
async def test_a_custom_endpoint_runs_with_the_client_settings() -> None:
    transport = _answer(_TEXT)
    shazam = Shazam(
        language="de",
        country="AT",
        transport=transport,
    )

    greeting = await shazam(_Greeting(name="Ada"))

    (request,) = transport.requests
    assert (greeting, request.url, dict(request.params)) == (
        "HELLO",
        "https://greeting.example.com/de/AT",
        {"name": "Ada"},
    )


@pytest.mark.asyncio
async def test_a_custom_endpoint_refuses_an_answer_of_another_content_type() -> None:
    shazam = Shazam(transport=_answer("application/json"))

    with pytest.raises(BadResponse, match="expected text/plain"):
        await shazam(_Greeting(name="Ada"))
