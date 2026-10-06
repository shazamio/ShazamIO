from typing import Final

import pytest

from scripts.probe_endpoints import Answer, Probe, Verdict, classify, probes, unprobed_url_names
from shazamio.apple import APPLE_TO_SHAZAM_CONTENT_TYPE
from shazamio.charts import CHART_CONTENT_TYPE

_CHART: Final[Probe] = Probe(
    url_name="TOP_WORLD_TRACKS",
    url="https://example.com/chart",
    content_type=CHART_CONTENT_TYPE,
)
_UNKNOWN_SLUG: Final[Probe] = Probe(
    url_name="TOP_WORLD_GENRE_TRACKS",
    url="https://example.com/chart/no-such-genre",
    content_type=CHART_CONTENT_TYPE,
    expected=Verdict.BAD_INPUT,
)
_A2ST: Final[Probe] = Probe(
    url_name="APPLE_IDS_TO_TRACK_KEYS",
    url="https://example.com/a2st",
    content_type=APPLE_TO_SHAZAM_CONTENT_TYPE,
)
_WEBSITE: Final[Answer] = Answer(
    status=200,
    content_type="text/html",
    body=b"<!doctype html>",
)
_CLEAN_MISS: Final[Answer] = Answer(
    status=404,
    content_type="application/octet-stream",
    body=b"",
)
_CSV: Final[Answer] = Answer(
    status=200,
    content_type=CHART_CONTENT_TYPE,
    body=b"1,Artist,Title",
)


def test_every_url_the_library_calls_has_a_probe() -> None:
    assert unprobed_url_names(probes()) == set()


@pytest.mark.parametrize(
    ("probe", "answer", "expected"),
    [
        pytest.param(_CHART, _CSV, Verdict.LIVE, id="live"),
        pytest.param(_CHART, _WEBSITE, Verdict.DEAD, id="website-shell"),
        pytest.param(_UNKNOWN_SLUG, _WEBSITE, Verdict.DEAD, id="website-shell-on-bad-input"),
        pytest.param(_UNKNOWN_SLUG, _CLEAN_MISS, Verdict.BAD_INPUT, id="clean-miss"),
        pytest.param(_UNKNOWN_SLUG, _CSV, Verdict.UNEXPECTED, id="bad-input-answered"),
        pytest.param(
            _CHART,
            Answer(
                status=204,
                content_type="application/octet-stream",
                body=b"",
            ),
            Verdict.UNEXPECTED,
            id="no-content",
        ),
        pytest.param(
            _A2ST,
            Answer(
                status=200,
                content_type=APPLE_TO_SHAZAM_CONTENT_TYPE,
                body=b'{"error":{"msg":"Could not fetch ids"}}',
            ),
            Verdict.UNEXPECTED,
            id="a2st-error-body",
        ),
    ],
)
def test_classify(probe: Probe, *, answer: Answer, expected: Verdict) -> None:
    assert classify(probe, answer=answer) is expected
