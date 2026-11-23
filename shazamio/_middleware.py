from collections.abc import Sequence
from functools import partial
from typing import Protocol

from shazamio._transport import Request, Response, Transport

__all__ = [
    "CallNext",
    "Middleware",
    "chain",
]


class CallNext(Protocol):
    __module__ = "shazamio"

    async def __call__(self, request: Request) -> Response:
        """Send `request` on down the chain, to the transport last."""


class Middleware(Protocol):
    """A step every request of one `Shazam` passes through, the first one outermost.

    It may change the request, answer it without `call_next`, call `call_next`
    more than once, or read the response on its way back.
    """

    __module__ = "shazamio"

    async def __call__(
        self,
        request: Request,
        *,
        call_next: CallNext,
    ) -> Response:
        """Hand `request` to `call_next` and return the response."""


def chain(
    middleware: Sequence[Middleware],
    *,
    transport: Transport,
) -> CallNext:
    call_next: CallNext = transport.send
    for step in reversed(middleware):
        call_next = partial(step, call_next=call_next)

    return call_next
