from typing import Final

import pytest

from shazamio._parsers import SearchAnswer, parse_apple_ids, parse_chart, parse_model
from shazamio.exceptions import BadPayload, NotFound

# The shape the endpoint really returns, as `_CHART_HEADER` in `shazamio._parsers` describes.
_CHART_CSV: Final[str] = (
    "﻿\n"
    '"Monday, 14 September 2026 [performance over the past 7 days]"\n'
    "Rank,Artist,Title\n"
    '1,"HUGEL, Imael Angel & Ultra Naté","Movin\' To The Sun"\n'
    '2,"Imael Angel","BAD TIMES"\n'
)
# Trimmed from a real answer: every song carries far more fields than `trackId`.
_SEARCH_ANSWER: Final[str] = (
    '{"resultCount":2,"results":['
    '{"wrapperType":"track","kind":"song","trackId":697195462,"trackName":"One More Time"},'
    '{"wrapperType":"track","kind":"song","trackId":697402071,"trackName":"One More Time (12 Mix)"}'
    "]}"
)


def test_the_preamble_is_skipped_and_every_row_is_read() -> None:
    tracks = parse_chart(_CHART_CSV)

    assert [track.model_dump() for track in tracks] == [
        {"rank": 1, "artist": "HUGEL, Imael Angel & Ultra Naté", "title": "Movin' To The Sun"},
        {"rank": 2, "artist": "Imael Angel", "title": "BAD TIMES"},
    ]


def test_a_row_with_a_field_count_unlike_the_header_is_skipped(
    caplog: pytest.LogCaptureFixture,
) -> None:
    payload: str = _CHART_CSV + (
        '3,"Imael Angel","BAD TIMES","Remix"\n4,"HUGEL"\n5,"HUGEL","Morenita"\n'
    )

    tracks = parse_chart(payload)

    assert [track.rank for track in tracks] == [1, 2, 5]
    assert [(record.message, vars(record)["row"]) for record in caplog.records] == [
        ("parse_chart.skip", ["3", "Imael Angel", "BAD TIMES", "Remix"]),
        ("parse_chart.skip", ["4", "HUGEL"]),
    ]


def test_a_body_without_the_header_is_rejected() -> None:
    with pytest.raises(BadPayload):
        parse_chart("<!doctype html>\n")


def test_a_mapping_is_read_as_served() -> None:
    assert parse_apple_ids('{"1125281672":"325127876"}') == {
        "1125281672": "325127876",
    }


def test_an_error_body_is_reported_as_bad_ids() -> None:
    with pytest.raises(NotFound, match="Could not fetch ids"):
        parse_apple_ids('{"error":{"msg":"Could not fetch ids"}}')


def test_a_body_that_is_not_json_is_rejected() -> None:
    with pytest.raises(BadPayload):
        parse_apple_ids("<!doctype html>\n")


def test_a_body_that_is_json_but_not_a_mapping_is_rejected() -> None:
    with pytest.raises(BadPayload):
        parse_apple_ids('["325127876"]')


def test_the_track_ids_are_read_in_apple_order() -> None:
    answer = parse_model(_SEARCH_ANSWER, model=SearchAnswer)

    assert [song.track_id for song in answer.results] == [697195462, 697402071]


def test_an_answer_without_results_is_rejected() -> None:
    with pytest.raises(BadPayload):
        parse_model("<!doctype html>\n", model=SearchAnswer)
