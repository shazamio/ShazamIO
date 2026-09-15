from collections.abc import AsyncIterator
from http import HTTPStatus
from typing import Final

import pytest
from aiohttp import web
from aiohttp.test_utils import TestServer

from shazamio.charts import CHART_CONTENT_TYPE
from shazamio.client import HTTPClient
from shazamio.exceptions import BadContentType, BadResponseStatus

_NOT_PUBLISHED: Final[str] = "/not-published"
_WEBSITE: Final[str] = "/website"


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

    app = web.Application()
    app.router.add_get(_NOT_PUBLISHED, not_published)
    app.router.add_get(_WEBSITE, the_website)

    test_server = TestServer(app)
    await test_server.start_server()

    yield test_server

    await test_server.close()


@pytest.mark.asyncio
async def test_a_chart_that_is_not_published_names_its_status(server: TestServer) -> None:
    with pytest.raises(BadResponseStatus, match="404"):
        await HTTPClient().request_text(
            str(server.make_url(_NOT_PUBLISHED)),
            content_type=CHART_CONTENT_TYPE,
        )


@pytest.mark.asyncio
async def test_a_path_answered_by_the_website_names_the_content_type(server: TestServer) -> None:
    with pytest.raises(BadContentType, match="text/html"):
        await HTTPClient().request_text(
            str(server.make_url(_WEBSITE)),
            content_type=CHART_CONTENT_TYPE,
        )
