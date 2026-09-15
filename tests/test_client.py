from typing import Final

import pytest

from shazamio.charts import CHART_CONTENT_TYPE
from shazamio.client import HTTPClient
from shazamio.exceptions import BadContentType, BadResponseStatus
from shazamio.misc import Request

_CHART_OF_NO_COUNTRY: Final[str] = (
    "https://www.shazam.com/services/charts/csv/top-200/not-a-country/"
)
_WEBSITE: Final[str] = "https://www.shazam.com/"


@pytest.mark.asyncio
async def test_a_chart_that_is_not_published_names_its_status() -> None:
    with pytest.raises(BadResponseStatus, match="404"):
        await HTTPClient().request_text(
            _CHART_OF_NO_COUNTRY,
            content_type=CHART_CONTENT_TYPE,
            headers=Request("en-US").headers(),
        )


@pytest.mark.asyncio
async def test_a_path_answered_by_the_website_names_the_content_type() -> None:
    with pytest.raises(BadContentType, match="text/html"):
        await HTTPClient().request_text(
            _WEBSITE,
            content_type=CHART_CONTENT_TYPE,
            headers=Request("en-US").headers(),
        )
