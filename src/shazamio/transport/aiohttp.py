import asyncio

from aiohttp import ClientError, ClientSession

from shazamio.exceptions import TransportError
from shazamio.transport.base import Request, Response, Transport

__all__ = [
    "AiohttpTransport",
]


async def _exchange(
    session: ClientSession,
    *,
    request: Request,
) -> Response:
    async with session.request(
        request.method,
        request.url,
        headers=request.headers,
        params=request.params,
        data=request.body,
        # A session built with `raise_for_status` raised `ClientResponseError`
        #  here, before `Shazam` saw the status, so a `503` was neither retried
        #  nor a `BadResponse`; the per-request flag wins over the session's:
        #  https://github.com/aio-libs/aiohttp/blob/f17c631bddcfd4ec712342db28f1d3381a3fec71/aiohttp/client.py#L1045-L1046
        raise_for_status=False,
    ) as response:
        # An error page in a broken charset is still a status to report.
        text = await response.text(errors="replace")

        return Response(
            status=response.status,
            content_type=response.content_type,
            text=text,
            headers=response.headers,
        )


class AiohttpTransport(Transport):
    """The default transport, on an `aiohttp` session.

    Pass `session` to route traffic your way, a proxy or SOCKS connector included;
    that session stays yours to close, and its `raise_for_status` is ignored.
    Without one, the transport opens its own pool on the first request and closes
    it in `close()`.
    """

    def __init__(self, *, session: ClientSession | None = None) -> None:
        self._session = session
        self._own_session: ClientSession | None = None
        self._loop: asyncio.AbstractEventLoop | None = None
        self._closed: bool = False

    async def send(self, request: Request) -> Response:
        session = self._ensure_session()

        # A total timeout raises a bare `TimeoutError`, no `ClientError`: on `aiohttp`
        #  3.14.5, `ClientTimeout(total=0.05)` against a handler sleeping 1 s did.
        try:
            return await _exchange(session, request=request)
        except (ClientError, TimeoutError) as er:
            msg = f"{request.url} sent no answer: {er!r}"
            raise TransportError(msg) from er

    async def close(self) -> None:
        self._closed = True

        if self._own_session is not None:
            await self._own_session.close()

    def _ensure_session(self) -> ClientSession:
        if self._closed:
            msg: str = "AiohttpTransport is closed"
            raise RuntimeError(msg)

        if self._session is not None:
            return self._session

        # Built on the first request and rebuilt when the loop changes: a
        #  `ClientSession` binds to the loop it is built on, so a client reused
        #  across two `asyncio.run` calls raised `RuntimeError: Event loop is
        #  closed`. The spent session is abandoned: closing it from the new loop
        #  marks it closed and still leaves its socket open.
        #  https://github.com/aio-libs/aiohttp/blob/5e392ce0456f5235a4ee6ad46f0e806df2f15873/aiohttp/client.py#L353
        loop = asyncio.get_running_loop()
        if self._own_session is None or self._loop is not loop:
            self._own_session = ClientSession()
            self._loop = loop

        return self._own_session
