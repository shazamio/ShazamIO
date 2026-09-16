from collections.abc import AsyncIterator
from http import HTTPStatus
from typing import Final

import pytest
from aiohttp import web
from aiohttp.test_utils import TestServer

from shazamio import Shazam
from shazamio.charts import CHART_CONTENT_TYPE
from shazamio.client import HTTPClient
from shazamio.exceptions import (
    BadContentType,
    BadResponseStatus,
    FailedDecodeJson,
    RateLimited,
)

_NOT_PUBLISHED: Final[str] = "/not-published"
_WEBSITE: Final[str] = "/website"
_THROTTLED: Final[str] = "/throttled"
_PEER: Final[str] = "/peer"


# Both guards are checked against a local server rather than against
#  `www.shazam.com`, which answers a GitHub runner's address with `403` where it
#  answers a workstation with `200 text/html`, so the live version of the
#  content-type test failed in CI alone.
@pytest.fixture
async def server() -> AsyncIterator[TestServer]:
    async def not_published(_request: web.Request) -> web.Response:
        return web.Response(status=HTTPStatus.NOT_FOUND)

    async def the_website(_request: web.Request) -> web.Response:
        return web.Response(
            text="<html></html>",
            content_type="text/html",
        )

    async def throttled(_request: web.Request) -> web.Response:
        return web.Response(
            status=HTTPStatus.TOO_MANY_REQUESTS,
            text="<html></html>",
            content_type="text/html",
        )

    async def peer(request: web.Request) -> web.Response:
        # The source port names the TCP connection the request arrived on, which
        #  is how the reuse test below sees whether anything was pooled.
        transport = request.transport
        assert transport is not None

        return web.json_response({"source_port": transport.get_extra_info("peername")[1]})

    app = web.Application()
    app.router.add_get(_NOT_PUBLISHED, not_published)
    app.router.add_get(_WEBSITE, the_website)
    app.router.add_get(_THROTTLED, throttled)
    app.router.add_get(_PEER, peer)

    test_server = TestServer(app)
    await test_server.start_server()

    yield test_server

    await test_server.close()


async def _source_port(client: HTTPClient, *, url: str) -> int:
    answer = await client.request("GET", url)
    assert isinstance(answer, dict)

    return int(answer["source_port"])


@pytest.mark.asyncio
async def test_a_chart_that_is_not_published_names_its_status(server: TestServer) -> None:
    async with HTTPClient() as client:
        with pytest.raises(BadResponseStatus, match="404"):
            await client.request_text(
                str(server.make_url(_NOT_PUBLISHED)),
                content_type=CHART_CONTENT_TYPE,
            )


@pytest.mark.asyncio
async def test_a_path_answered_by_the_website_names_the_content_type(server: TestServer) -> None:
    async with HTTPClient() as client:
        with pytest.raises(BadContentType, match="text/html"):
            await client.request_text(
                str(server.make_url(_WEBSITE)),
                content_type=CHART_CONTENT_TYPE,
            )


@pytest.mark.asyncio
async def test_a_throttled_request_names_the_rate_limit(server: TestServer) -> None:
    async with HTTPClient() as client:
        with pytest.raises(RateLimited, match="rate limited"):
            await client.request("GET", str(server.make_url(_THROTTLED)))


# The control for the test above: both answers are `text/html`, and only the
#  throttled one is a rate limit. Without it a guard firing on every undecodable
#  body would pass.
@pytest.mark.asyncio
async def test_an_undecodable_body_that_is_not_throttling_still_names_the_decoder(
    server: TestServer,
) -> None:
    async with HTTPClient() as client:
        with pytest.raises(FailedDecodeJson, match="status=200"):
            await client.request("GET", str(server.make_url(_WEBSITE)))


@pytest.mark.asyncio
async def test_sequential_requests_share_one_connection(server: TestServer) -> None:
    url = str(server.make_url(_PEER))

    async with HTTPClient() as client:
        source_ports = {await _source_port(client, url=url) for _ in range(3)}

    assert len(source_ports) == 1


@pytest.mark.asyncio
async def test_a_request_after_a_close_names_the_closed_session(server: TestServer) -> None:
    url = str(server.make_url(_PEER))

    client = HTTPClient()
    await _source_port(client, url=url)
    await client.close()

    with pytest.raises(RuntimeError, match="Session is closed"):
        await client.request("GET", url)


@pytest.mark.asyncio
async def test_closing_a_client_that_never_made_a_request_is_not_an_error() -> None:
    # Nothing to assert past not raising: the session is built on the first
    #  request, so a client that made none has nothing to close.
    await HTTPClient().close()


@pytest.mark.asyncio
async def test_shazam_closes_the_client_it_built(server: TestServer) -> None:
    url = str(server.make_url(_PEER))
    shazam = Shazam()

    async with shazam:
        await shazam.http_client.request("GET", url)

    with pytest.raises(RuntimeError, match="Session is closed"):
        await shazam.http_client.request("GET", url)


@pytest.mark.asyncio
async def test_shazam_leaves_a_client_it_was_given_open(server: TestServer) -> None:
    url = str(server.make_url(_PEER))
    given = HTTPClient()

    async with Shazam(http_client=given):
        pass

    # Still usable afterwards: its lifetime belongs to whoever built it.
    await _source_port(given, url=url)
    await given.close()
