import asyncio
import dataclasses
import math
from collections.abc import Sequence
from http import HTTPMethod, HTTPStatus
from typing import Final

import pytest

from shazamio import Request, Response, Retry, TransportError
from shazamio._retry import _delay, send_with_retry
from shazamio.testing import MockTransport

_REQUEST: Final[Request] = Request(
    method=HTTPMethod.POST,
    url="https://amp.shazam.com/tag",
)
# The defaults with no wait between attempts, so twenty of them take no time.
_NO_WAIT: Final[Retry] = dataclasses.replace(Retry(), start_delay=0.0)
_SUCCESS: Final[Response] = Response(
    status=HTTPStatus.OK,
    content_type="application/json",
    text="{}",
)


def _answers(statuses: Sequence[int]) -> MockTransport:
    """Answer with each status in turn, then with the last one for good."""
    remaining = list(statuses)

    def answer(_request: Request) -> Response:
        return Response(
            status=remaining.pop(0) if len(remaining) > 1 else remaining[0],
            content_type="application/json",
            text="{}",
        )

    return MockTransport(answer)


def _failed(
    status: int,
    *,
    retry_after: str | None = None,
) -> Response:
    return Response(
        status=status,
        content_type="text/html",
        text="",
        headers={} if retry_after is None else {"Retry-After": retry_after},
    )


# The waits `aiohttp_retry.ExponentialRetry(start_timeout=0.1, max_timeout=60)`
#  slept, the options this replaces: `0.1 * 2 ** attempt`, the first after attempt 1.
@pytest.mark.parametrize(
    ("attempt", "seconds"),
    [
        pytest.param(1, 0.2, id="first"),
        pytest.param(2, 0.4, id="second"),
        pytest.param(9, 51.2, id="last-below-the-cap"),
        pytest.param(10, 60.0, id="capped"),
        pytest.param(19, 60.0, id="last"),
    ],
)
def test_the_default_backoff_doubles_from_a_fifth_of_a_second_up_to_a_minute(
    *,
    attempt: int,
    seconds: float,
) -> None:
    delay = _delay(
        Retry(),
        attempt=attempt,
        response=_failed(HTTPStatus.SERVICE_UNAVAILABLE),
    )

    assert math.isclose(delay, seconds)


@pytest.mark.parametrize(
    ("retry_after", "seconds"),
    [
        pytest.param("3", 3.0, id="seconds"),
        pytest.param("3600", 60.0, id="capped"),
        pytest.param("Wed, 21 Oct 2026 07:28:00 GMT", 0.2, id="http-date-falls-back"),
    ],
)
def test_retry_after_replaces_the_backoff(
    *,
    retry_after: str,
    seconds: float,
) -> None:
    delay = _delay(
        Retry(),
        attempt=1,
        response=_failed(HTTPStatus.TOO_MANY_REQUESTS, retry_after=retry_after),
    )

    assert math.isclose(delay, seconds)


# A `Transport` over `httpx` hands the header names over lowercased.
def test_a_lowercase_retry_after_replaces_the_backoff() -> None:
    response = Response(
        status=HTTPStatus.TOO_MANY_REQUESTS,
        content_type="text/html",
        text="",
        headers={"retry-after": "3"},
    )

    delay = _delay(
        Retry(),
        attempt=1,
        response=response,
    )

    assert math.isclose(delay, 3.0)


# `factor ** attempt` alone passes the float range here, whatever the cap.
@pytest.mark.parametrize(
    ("start_delay", "seconds"),
    [
        pytest.param(0.1, 60.0, id="capped"),
        pytest.param(0.0, 0.0, id="no-wait"),
    ],
)
def test_a_backoff_past_the_float_range_is_capped(
    *,
    start_delay: float,
    seconds: float,
) -> None:
    retry = Retry(
        attempts=400,
        start_delay=start_delay,
        factor=10.0,
    )

    delay = _delay(
        retry,
        attempt=309,
        response=_failed(HTTPStatus.SERVICE_UNAVAILABLE),
    )

    assert math.isclose(delay, seconds)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("responses", "waits"),
    [
        pytest.param(
            [
                _failed(HTTPStatus.SERVICE_UNAVAILABLE),
                _failed(HTTPStatus.SERVICE_UNAVAILABLE),
                _SUCCESS,
            ],
            [0.2, 0.4],
            id="backoff",
        ),
        pytest.param(
            [_failed(HTTPStatus.TOO_MANY_REQUESTS, retry_after="3"), _SUCCESS],
            [3.0],
            id="retry-after",
        ),
    ],
)
async def test_a_retry_waits_the_schedule_between_attempts(
    monkeypatch: pytest.MonkeyPatch,
    *,
    responses: list[Response],
    waits: list[float],
) -> None:
    remaining = list(responses)
    slept: list[float] = []

    async def sleep(delay: float) -> None:
        slept.append(delay)

    monkeypatch.setattr(asyncio, "sleep", sleep)

    await send_with_retry(
        _REQUEST,
        transport=MockTransport(lambda _request: remaining.pop(0)),
        retry=Retry(),
    )

    assert slept == pytest.approx(waits)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "status",
    [
        pytest.param(HTTPStatus.TOO_MANY_REQUESTS, id="429"),
        pytest.param(HTTPStatus.INTERNAL_SERVER_ERROR, id="500"),
        pytest.param(HTTPStatus.NOT_IMPLEMENTED, id="501"),
        pytest.param(HTTPStatus.SERVICE_UNAVAILABLE, id="503"),
    ],
)
async def test_a_failing_status_is_sent_twenty_times_and_the_last_answer_returned(
    status: HTTPStatus,
) -> None:
    transport = _answers([status])

    response = await send_with_retry(
        _REQUEST,
        transport=transport,
        retry=_NO_WAIT,
    )

    assert (len(transport.requests), response.status) == (20, status)


@pytest.mark.asyncio
async def test_a_retry_stops_at_the_first_answer_outside_the_statuses() -> None:
    transport = _answers([HTTPStatus.SERVICE_UNAVAILABLE, HTTPStatus.OK])

    response = await send_with_retry(
        _REQUEST,
        transport=transport,
        retry=_NO_WAIT,
    )

    assert (len(transport.requests), response.status) == (2, HTTPStatus.OK)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "status",
    [
        pytest.param(HTTPStatus.NOT_FOUND, id="404"),
        pytest.param(HTTPStatus.FORBIDDEN, id="403"),
    ],
)
async def test_a_client_error_is_sent_once(status: HTTPStatus) -> None:
    transport = _answers([status])

    await send_with_retry(
        _REQUEST,
        transport=transport,
        retry=_NO_WAIT,
    )

    assert len(transport.requests) == 1


def test_a_retry_sending_nothing_is_refused() -> None:
    with pytest.raises(ValueError, match="at least once"):
        Retry(attempts=0)


class _Unreachable:
    """Raise `TransportError` `failures` times, then answer `200`."""

    def __init__(self, *, failures: int) -> None:
        self._failures = failures
        self._calls: int = 0

    @property
    def calls(self) -> int:
        return self._calls

    async def send(self, _request: Request) -> Response:
        self._calls += 1

        if self._calls <= self._failures:
            msg: str = "connection refused"
            raise TransportError(msg)

        return _SUCCESS


@pytest.mark.asyncio
async def test_a_transport_error_is_raised_at_once_by_default() -> None:
    transport = _Unreachable(failures=1)

    with pytest.raises(TransportError, match="refused"):
        await send_with_retry(
            _REQUEST,
            transport=transport,
            retry=_NO_WAIT,
        )

    assert transport.calls == 1


@pytest.mark.asyncio
async def test_a_transport_error_is_retried_when_asked() -> None:
    transport = _Unreachable(failures=2)
    retry = dataclasses.replace(_NO_WAIT, on_transport_error=True)

    response = await send_with_retry(
        _REQUEST,
        transport=transport,
        retry=retry,
    )

    assert (transport.calls, response.status) == (3, HTTPStatus.OK)


@pytest.mark.asyncio
async def test_the_last_transport_error_is_raised_after_every_attempt() -> None:
    transport = _Unreachable(failures=3)
    retry = Retry(
        attempts=3,
        start_delay=0.0,
        on_transport_error=True,
    )

    with pytest.raises(TransportError, match="refused"):
        await send_with_retry(
            _REQUEST,
            transport=transport,
            retry=retry,
        )

    assert transport.calls == 3
