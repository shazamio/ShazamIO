import asyncio
from http import HTTPStatus
from typing import Final

import pytest

from shazamio import BadResponse, CallNext, Request, Response, Shazam
from shazamio.testing import MockTransport

_VIDEO: Final[str] = (
    '{"caption": "", "image": {"dimensions": {"width": 0, "height": 0}, "url": ""}, "actions": []}'
)
_LINK: Final[str] = "https://cdn.shazam.com/video/v3/-/GB/iphone/1/youtube/video"


def _video(_request: Request) -> Response:
    return Response(
        status=HTTPStatus.OK,
        content_type="application/json",
        text=_VIDEO,
    )


def _unavailable(_request: Request) -> Response:
    return Response(
        status=HTTPStatus.SERVICE_UNAVAILABLE,
        content_type="text/html",
        text="",
    )


class _Recorder:
    def __init__(
        self,
        name: str,
        *,
        steps: list[str],
    ) -> None:
        self._name = name
        self._steps = steps

    async def __call__(
        self,
        request: Request,
        *,
        call_next: CallNext,
    ) -> Response:
        self._steps.append(f"{self._name} in")
        response = await call_next(request)
        self._steps.append(f"{self._name} out")

        return response


@pytest.mark.asyncio
async def test_the_first_middleware_wraps_the_ones_after_it() -> None:
    steps: list[str] = []
    shazam = Shazam(
        transport=MockTransport(_video),
        middleware=[
            _Recorder("outer", steps=steps),
            _Recorder("inner", steps=steps),
        ],
    )

    await shazam.get_youtube_data(_LINK)

    assert steps == ["outer in", "inner in", "inner out", "outer out"]


@pytest.mark.asyncio
async def test_a_middleware_can_answer_without_the_transport() -> None:
    async def cached(
        request: Request,
        *,
        call_next: CallNext,  # noqa: ARG001
    ) -> Response:
        return _video(request)

    transport = MockTransport(_unavailable)
    shazam = Shazam(
        transport=transport,
        middleware=[cached],
    )

    video = await shazam.get_youtube_data(_LINK)

    assert (video.caption, transport.requests) == ("", [])


# `()` is falsy, so a client reading it as "not given" retries the `503` with
#  the default backoff and runs into the timeout.
@pytest.mark.asyncio
async def test_no_middleware_sends_each_request_once() -> None:
    transport = MockTransport(_unavailable)
    shazam = Shazam(
        transport=transport,
        middleware=(),
    )

    async with asyncio.timeout(1):
        with pytest.raises(BadResponse, match="503"):
            await shazam.get_youtube_data(_LINK)

    assert len(transport.requests) == 1


@pytest.mark.asyncio
async def test_a_client_without_middleware_retries_by_default() -> None:
    def unavailable_for_now(_request: Request) -> Response:
        return Response(
            status=HTTPStatus.SERVICE_UNAVAILABLE,
            content_type="text/html",
            text="",
            headers={"Retry-After": "0"},
        )

    transport = MockTransport(unavailable_for_now)
    shazam = Shazam(transport=transport)

    with pytest.raises(BadResponse, match="503"):
        await shazam.get_youtube_data(_LINK)

    assert len(transport.requests) == 20
