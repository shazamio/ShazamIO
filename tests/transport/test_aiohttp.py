import asyncio
import json
import socket
from collections.abc import AsyncGenerator
from http import HTTPMethod, HTTPStatus
from typing import Final

import pytest
from aiohttp import ClientSession, ClientTimeout, web
from aiohttp.test_utils import TestServer

from shazamio import (
    AiohttpTransport,
    BadResponse,
    Request,
    Response,
    Retry,
    Shazam,
    Transport,
    TransportError,
)

_JSON: Final[str] = "application/json"
_PEER: Final[str] = "/peer"
_VIDEO: Final[str] = "/video"
_UNAVAILABLE: Final[str] = "/unavailable"
_ECHO: Final[str] = "/echo"
_BROKEN_CHARSET: Final[str] = "/broken-charset"
_MIXED_CASE_TYPE: Final[str] = "/mixed-case-type"
_SLOW: Final[str] = "/slow"
_UNROUTABLE_HOST: Final[str] = "shazam.invalid"
_ATTEMPTS: Final[web.AppKey[list[str]]] = web.AppKey("attempts")
_CONNECTIONS: Final[web.AppKey[list[asyncio.BaseTransport]]] = web.AppKey("connections")
# What every transport owes `Shazam`, run against each one the package ships.
_EVERY_TRANSPORT: Final[pytest.MarkDecorator] = pytest.mark.parametrize(
    "factory",
    [
        pytest.param(AiohttpTransport, id="aiohttp"),
    ],
)


def _application() -> web.Application:
    async def peer(request: web.Request) -> web.Response:
        # The source port names the TCP connection the request arrived on, which
        #  is how the reuse test below sees whether anything was pooled.
        transport = request.transport
        assert transport is not None

        return web.json_response({"source_port": transport.get_extra_info("peername")[1]})

    # A video answer whose caption names the host the request was sent to, so a
    #  test can go through the public `Shazam` and still see where it landed.
    async def video(request: web.Request) -> web.Response:
        assert request.transport is not None
        request.app[_CONNECTIONS].append(request.transport)

        return web.json_response(
            {
                "caption": request.host,
                "image": {"dimensions": {"width": 0, "height": 0}, "url": ""},
                "actions": [],
            },
        )

    async def unavailable(request: web.Request) -> web.Response:
        request.app[_ATTEMPTS].append(request.path)

        return web.Response(
            status=HTTPStatus.SERVICE_UNAVAILABLE,
            headers={"Retry-After": "0"},
        )

    async def echo(request: web.Request) -> web.Response:
        return web.json_response(
            {
                "content_type": request.content_type,
                "body": await request.json(),
                "query": dict(request.query),
            },
        )

    async def broken_charset(_request: web.Request) -> web.Response:
        return web.Response(
            status=HTTPStatus.SERVICE_UNAVAILABLE,
            body=b"\xff\xfe",
            content_type="text/html",
            charset="utf-8",
        )

    async def mixed_case_type(_request: web.Request) -> web.Response:
        return web.Response(
            text="{}",
            headers={"Content-Type": "Application/JSON ; charset=utf-8"},
        )

    async def slow(_request: web.Request) -> web.Response:
        await asyncio.sleep(1)

        return web.json_response({})

    app = web.Application()
    app[_ATTEMPTS] = []
    app[_CONNECTIONS] = []

    app.router.add_get(_UNAVAILABLE, unavailable)
    app.router.add_get(_PEER, peer)
    app.router.add_get(_VIDEO, video)
    app.router.add_get(_BROKEN_CHARSET, broken_charset)
    app.router.add_get(_MIXED_CASE_TYPE, mixed_case_type)
    app.router.add_get(_SLOW, slow)

    app.router.add_post(_ECHO, echo)

    return app


# Checked against a local server rather than against `www.shazam.com`, which
#  answers a GitHub runner's address with `403` where it answers a workstation
#  with `200 text/html`, so a live version failed in CI alone.
@pytest.fixture
async def server() -> AsyncGenerator[TestServer]:
    test_server = TestServer(_application())
    await test_server.start_server()

    yield test_server

    await test_server.close()


def _get(url: str) -> Request:
    return Request(
        method=HTTPMethod.GET,
        url=url,
    )


async def _source_port(
    transport: Transport,
    *,
    url: str,
) -> int:
    response = await transport.send(_get(url))

    return int(json.loads(response.text)["source_port"])


@pytest.mark.asyncio
@_EVERY_TRANSPORT
async def test_sequential_requests_share_one_connection(
    server: TestServer,
    *,
    factory: type[Transport],
) -> None:
    url = str(server.make_url(_PEER))
    transport = factory()

    source_ports = {await _source_port(transport, url=url) for _ in range(3)}
    await transport.close()

    assert len(source_ports) == 1


@pytest.mark.asyncio
@_EVERY_TRANSPORT
async def test_a_post_arrives_with_its_body_query_and_content_type(
    server: TestServer,
    *,
    factory: type[Transport],
) -> None:
    transport = factory()

    response = await transport.send(
        Request(
            method=HTTPMethod.POST,
            url=str(server.make_url(_ECHO)),
            headers={"Content-Type": _JSON},
            params={"limit": 5},
            body=b'{"signature": {"uri": "data:"}}',
        ),
    )
    await transport.close()

    assert (response.status, response.content_type) == (HTTPStatus.OK, _JSON)
    assert json.loads(response.text) == {
        "content_type": _JSON,
        "body": {"signature": {"uri": "data:"}},
        "query": {"limit": "5"},
    }


# The full message tells the guard from `aiohttp`'s own `Session is closed`,
#  which an own pool raises without it. A given session stays open, so only the
#  guard refuses there.
@pytest.mark.asyncio
@pytest.mark.parametrize(
    "given_session",
    [pytest.param(False, id="own-pool"), pytest.param(True, id="given-session")],
)
async def test_a_request_after_a_close_is_refused(
    server: TestServer,
    *,
    given_session: bool,
) -> None:
    url = str(server.make_url(_PEER))

    async with ClientSession() as session:
        transport = AiohttpTransport(session=session if given_session else None)
        await _source_port(transport, url=url)
        await transport.close()

        with pytest.raises(RuntimeError, match="AiohttpTransport is closed"):
            await _source_port(transport, url=url)


@pytest.mark.asyncio
async def test_closing_a_transport_leaves_the_session_it_was_given_open(
    server: TestServer,
) -> None:
    async with ClientSession() as session:
        transport = AiohttpTransport(session=session)
        await _source_port(transport, url=str(server.make_url(_PEER)))
        await transport.close()

        assert not session.closed


@pytest.mark.asyncio
async def test_a_session_raising_for_status_still_hands_over_the_status(
    server: TestServer,
) -> None:
    async with ClientSession(raise_for_status=True) as session:
        response = await AiohttpTransport(session=session).send(
            _get(str(server.make_url(_UNAVAILABLE))),
        )

    assert response.status == HTTPStatus.SERVICE_UNAVAILABLE


@pytest.mark.asyncio
@_EVERY_TRANSPORT
async def test_a_response_carries_the_retry_after_the_service_sent(
    server: TestServer,
    *,
    factory: type[Transport],
) -> None:
    transport = factory()

    response = await transport.send(_get(str(server.make_url(_UNAVAILABLE))))
    await transport.close()

    assert response.headers["Retry-After"] == "0"


@pytest.mark.asyncio
@_EVERY_TRANSPORT
async def test_an_error_page_in_a_broken_charset_still_hands_over_the_status(
    server: TestServer,
    *,
    factory: type[Transport],
) -> None:
    transport = factory()

    response = await transport.send(_get(str(server.make_url(_BROKEN_CHARSET))))
    await transport.close()

    assert response.status == HTTPStatus.SERVICE_UNAVAILABLE


# `Shazam` compares the media type alone, as the service spells it in lowercase.
@pytest.mark.asyncio
@_EVERY_TRANSPORT
async def test_the_content_type_is_the_lowercase_media_type(
    server: TestServer,
    *,
    factory: type[Transport],
) -> None:
    transport = factory()

    response = await transport.send(_get(str(server.make_url(_MIXED_CASE_TYPE))))
    await transport.close()

    assert response.content_type == _JSON


def _closed_port() -> int:
    with socket.socket() as listener:
        listener.bind(("127.0.0.1", 0))

        return int(listener.getsockname()[1])


@pytest.mark.asyncio
@_EVERY_TRANSPORT
async def test_a_refused_connection_raises_a_transport_error(*, factory: type[Transport]) -> None:
    transport = factory()

    with pytest.raises(TransportError, match="sent no answer") as raised:
        await transport.send(_get(f"http://127.0.0.1:{_closed_port()}/"))

    await transport.close()

    assert raised.value.__cause__ is not None


@pytest.mark.asyncio
async def test_a_timeout_of_the_given_session_raises_a_transport_error(
    server: TestServer,
) -> None:
    async with ClientSession(timeout=ClientTimeout(total=0.05)) as session:
        transport = AiohttpTransport(session=session)

        with pytest.raises(TransportError, match="sent no answer"):
            await transport.send(_get(str(server.make_url(_SLOW))))


@pytest.mark.asyncio
@_EVERY_TRANSPORT
async def test_closing_a_transport_that_never_made_a_request_is_not_an_error(
    *,
    factory: type[Transport],
) -> None:
    # Nothing to assert past not raising: the pool is built on the first
    #  request, so a transport that made none has nothing to close.
    await factory().close()


@pytest.mark.asyncio
async def test_shazam_leaves_a_session_it_was_given_open(server: TestServer) -> None:
    url = str(server.make_url(_VIDEO))

    async with ClientSession() as session:
        async with Shazam(transport=AiohttpTransport(session=session)) as shazam:
            await shazam.get_youtube_data(link=url)

        assert not session.closed

        async with session.get(url) as response:
            assert response.status == HTTPStatus.OK


@pytest.mark.asyncio
async def test_one_transport_serves_two_shazam_clients_in_turn(server: TestServer) -> None:
    url = str(server.make_url(_VIDEO))
    transport = AiohttpTransport()

    for _ in range(2):
        async with Shazam(transport=transport) as shazam:
            await shazam.get_youtube_data(link=url)

    await transport.close()


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "given_session",
    [pytest.param(False, id="own-pool"), pytest.param(True, id="given-session")],
)
async def test_shazam_retries_with_the_options_it_was_given(
    server: TestServer,
    *,
    given_session: bool,
) -> None:
    async with ClientSession() as session:
        shazam = Shazam(
            transport=AiohttpTransport(session=session if given_session else None),
            retry=Retry(attempts=2),
        )

        # The default options retry twenty times, so ignoring the given ones
        #  fails on the attempt count below.
        async with shazam, asyncio.timeout(5):
            with pytest.raises(BadResponse, match="503"):
                await shazam.get_youtube_data(link=str(server.make_url(_UNAVAILABLE)))

    assert server.app[_ATTEMPTS] == [_UNAVAILABLE, _UNAVAILABLE]


@pytest.mark.asyncio
async def test_shazam_closes_the_pool_it_opened(server: TestServer) -> None:
    async with Shazam() as shazam:
        await shazam.get_youtube_data(link=str(server.make_url(_VIDEO)))

    # The server sees the socket close a few loop iterations after the client
    #  closes it, and its transport offers a flag to read but no event to await.
    (connection,) = server.app[_CONNECTIONS]
    async with asyncio.timeout(1):
        while not connection.is_closing():  # noqa: ASYNC110
            await asyncio.sleep(0.01)


# A proxy is configured on the session, the one way traffic is routed: the
#  request names an unroutable host and still lands on the local server, which
#  sees that host in the absolute-form request line a proxy receives.
@pytest.mark.asyncio
async def test_a_request_goes_through_the_proxy_of_the_given_session(server: TestServer) -> None:
    async with (
        ClientSession(proxy=str(server.make_url("/"))) as session,
        Shazam(transport=AiohttpTransport(session=session)) as shazam,
    ):
        video = await shazam.get_youtube_data(link=f"http://{_UNROUTABLE_HOST}{_VIDEO}")

    assert video.caption == _UNROUTABLE_HOST


async def _one_request_on_its_own_server(transport: Transport) -> Response:
    test_server = TestServer(_application())
    await test_server.start_server()

    try:
        return await transport.send(_get(str(test_server.make_url(_PEER))))
    finally:
        await test_server.close()


# Synchronous on purpose: the test owns both loops, the way a caller keeping one
#  `Shazam` at module scope and calling `asyncio.run` per song does; the
#  comment in `AiohttpTransport._ensure_session` says what the second call used
#  to raise.
@_EVERY_TRANSPORT
def test_one_transport_answers_across_two_event_loops(*, factory: type[Transport]) -> None:
    transport = factory()

    asyncio.run(_one_request_on_its_own_server(transport))
    asyncio.run(_one_request_on_its_own_server(transport))
    asyncio.run(transport.close())


@_EVERY_TRANSPORT
def test_a_closed_transport_stays_closed_in_a_new_event_loop(*, factory: type[Transport]) -> None:
    transport = factory()

    async def request_then_close() -> None:
        await _one_request_on_its_own_server(transport)
        await transport.close()

    asyncio.run(request_then_close())

    with pytest.raises(RuntimeError, match="closed"):
        asyncio.run(_one_request_on_its_own_server(transport))
