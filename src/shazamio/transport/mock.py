"""Test doubles for code that calls `Shazam`."""

from collections.abc import Sequence
from typing import Protocol

from shazamio.transport.base import Request, Response, Transport

__all__ = [
    "Handler",
    "MockTransport",
]


class Handler(Protocol):
    def __call__(self, request: Request) -> Response:
        """Answer `request`."""


class MockTransport(Transport):
    """Sends nothing: `handler` answers every request, and `requests` keeps each one.

    `Shazam(transport=MockTransport(handler))` then runs its retry, checks and
    parses the answers as it does the service's.
    """

    def __init__(self, handler: Handler) -> None:
        self._handler = handler
        self._requests: list[Request] = []

    @property
    def requests(self) -> Sequence[Request]:
        return self._requests

    async def send(self, request: Request) -> Response:
        self._requests.append(request)

        return self._handler(request)

    async def close(self) -> None:
        """Nothing to release."""
