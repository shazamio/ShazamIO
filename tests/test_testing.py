import json
from http import HTTPMethod, HTTPStatus
from typing import Final

import pytest

from shazamio import Request, Response, Shazam
from shazamio.testing import MockTransport

_TRACK: Final[str] = json.dumps(
    {"key": "53982678", "title": "I Will Survive", "subtitle": "Gloria Gaynor"}
)
_TRACK_PATH: Final[str] = "/track/53982678"


@pytest.mark.asyncio
async def test_a_mock_transport_answers_shazam_and_keeps_the_request() -> None:
    def answer(_request: Request) -> Response:
        return Response(
            status=HTTPStatus.OK,
            content_type="application/json",
            text=_TRACK,
        )

    transport = MockTransport(answer)

    async with Shazam(transport=transport) as shazam:
        track = await shazam.track_about(53982678)

    (request,) = transport.requests
    assert (track.title, request.method) == ("I Will Survive", HTTPMethod.GET)
    assert request.url.partition("?")[0].endswith(_TRACK_PATH)
