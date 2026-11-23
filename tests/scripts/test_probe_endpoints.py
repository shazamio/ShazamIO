from http import HTTPMethod
from typing import Final

import pytest

from scripts.probe_endpoints import (
    Exchange,
    Outcome,
    Probe,
    Verdict,
    classify,
    probes,
    unprobed_methods,
)
from shazamio import NotFound, Request, Response, Shazam

_CHART: Final[Probe] = Probe(
    method=Shazam.top_tracks.__name__,
    label="top_tracks()",
    call=Shazam.top_tracks,
)
_UNOFFERED_GENRE: Final[Probe] = Probe(
    method=Shazam.top_tracks.__name__,
    label="top_tracks('RU', genre=rock)",
    call=Shazam.top_tracks,
    expected=Verdict.BAD_INPUT,
)
_REQUEST: Final[Request] = Request(
    method=HTTPMethod.GET,
    url="https://example.com/chart",
)


def _answered(
    *,
    status: int,
    content_type: str,
    text: str,
    error: NotFound | None = None,
) -> Outcome:
    response = Response(
        status=status,
        content_type=content_type,
        text=text,
    )
    exchange = Exchange(
        request=_REQUEST,
        response=response,
    )

    return Outcome(
        exchanges=[exchange],
        error=error,
    )


_CSV: Final[Outcome] = _answered(
    status=200,
    content_type="text/csv",
    text="1,Artist,Title",
)
_WEBSITE: Final[Outcome] = _answered(
    status=200,
    content_type="text/html",
    text="<!doctype html>",
    error=NotFound("the website answered"),
)
_CLEAN_MISS: Final[Outcome] = _answered(
    status=404,
    content_type="application/octet-stream",
    text="",
    error=NotFound("answered 404"),
)
_NO_CONTENT: Final[Outcome] = _answered(
    status=204,
    content_type="application/octet-stream",
    text="",
    error=NotFound("answered 204"),
)


def test_every_public_method_has_a_probe() -> None:
    assert unprobed_methods(probes()) == set()


@pytest.mark.parametrize(
    ("probe", "outcome", "expected"),
    [
        pytest.param(_CHART, _CSV, Verdict.LIVE, id="live"),
        pytest.param(_CHART, _WEBSITE, Verdict.DEAD, id="website-shell"),
        pytest.param(_UNOFFERED_GENRE, _WEBSITE, Verdict.DEAD, id="website-shell-on-bad-input"),
        pytest.param(_UNOFFERED_GENRE, _CLEAN_MISS, Verdict.BAD_INPUT, id="clean-miss"),
        pytest.param(_UNOFFERED_GENRE, _CSV, Verdict.UNEXPECTED, id="bad-input-answered"),
        pytest.param(_CHART, _NO_CONTENT, Verdict.UNEXPECTED, id="no-content"),
        pytest.param(
            _CHART,
            Outcome(
                exchanges=[],
                error=NotFound("no request sent"),
            ),
            Verdict.UNEXPECTED,
            id="raised-before-sending",
        ),
    ],
)
def test_classify(
    probe: Probe,
    *,
    outcome: Outcome,
    expected: Verdict,
) -> None:
    assert classify(probe, outcome=outcome) is expected
