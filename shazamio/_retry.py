import asyncio
import logging
from dataclasses import dataclass
from http import HTTPStatus
from typing import Final

from shazamio._exceptions import TransportError
from shazamio._middleware import CallNext
from shazamio._transport import Request, Response

__all__ = [
    "Retry",
]

logger = logging.getLogger(name=__name__)


_RETRIED_STATUSES: Final[frozenset[int]] = frozenset(
    {HTTPStatus.TOO_MANY_REQUESTS.value, *range(HTTPStatus.INTERNAL_SERVER_ERROR, 600)},
)


@dataclass(frozen=True, kw_only=True)
class Retry:
    """The middleware repeating a request answered with a status in `statuses`.

    With `on_transport_error`, a request that raised `TransportError` is repeated
    too. After attempt `n` it waits `min(start_delay * factor ** n, max_delay)`
    seconds, or the `Retry-After` the answer names, capped at `max_delay`. The last
    attempt's answer or error goes back as it came. `Retry(attempts=1)` sends every
    request once.
    """

    __module__ = "shazamio"

    attempts: int = 20
    start_delay: float = 0.1
    factor: float = 2.0
    max_delay: float = 60.0
    statuses: frozenset[int] = _RETRIED_STATUSES
    on_transport_error: bool = False

    def __post_init__(self) -> None:
        if self.attempts < 1:
            msg = f"attempts={self.attempts}: a request is sent at least once"
            raise ValueError(msg)

    async def __call__(
        self,
        request: Request,
        *,
        call_next: CallNext,
    ) -> Response:
        for attempt in range(1, self.attempts):
            response = await self._answer(request, call_next=call_next)

            if response is not None and response.status not in self.statuses:
                return response

            delay = _delay(
                self,
                attempt=attempt,
                response=response,
            )

            logging_extra = {
                "url": request.url,
                "status": None if response is None else response.status,
                "attempt": attempt,
                "delay": delay,
            }
            logger.debug("Retry.call.retry", extra=logging_extra)

            await asyncio.sleep(delay)

        return await call_next(request)

    async def _answer(
        self,
        request: Request,
        *,
        call_next: CallNext,
    ) -> Response | None:
        """The response, or `None` for a `TransportError` this retry repeats."""
        try:
            return await call_next(request)
        except TransportError:
            if not self.on_transport_error:
                raise

            return None


def _delay(
    retry: Retry,
    *,
    attempt: int,
    response: Response | None,
) -> float:
    headers = {} if response is None else response.headers

    # Header names are case-insensitive, and `httpx` hands them over lowercased.
    retry_after = next(
        (value for name, value in headers.items() if name.lower() == "retry-after"),
        None,
    )

    # Only the delay-seconds form; an HTTP date falls back to the backoff.
    if retry_after is not None and retry_after.isdecimal():
        return min(float(retry_after), retry.max_delay)

    return _backoff(retry, attempt=attempt)


def _backoff(
    retry: Retry,
    *,
    attempt: int,
) -> float:
    # A float power past about `1.8e308` raises instead of returning `inf`:
    #  `print(2.0**1024)` gives `OverflowError: (34, 'Numerical result out of range')`.
    try:
        backoff: float = retry.start_delay * retry.factor**attempt
    except OverflowError:
        backoff = retry.max_delay if retry.start_delay > 0 else 0.0

    return min(backoff, retry.max_delay)
