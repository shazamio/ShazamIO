from typing import Final

import pytest

from shazamio import GenreMusic, Shazam
from shazamio.charts import parse_chart_csv
from shazamio.exceptions import BadParseData

# The shape the endpoint really returns: a byte order mark, a blank line and a
#  quoted caption before the header row.
_CHART_CSV: Final[str] = (
    "﻿\n"
    '"Monday, 14 September 2026 [performance over the past 7 days]"\n'
    "Rank,Artist,Title\n"
    '1,"HUGEL, Imael Angel & Ultra Naté","Movin\' To The Sun"\n'
    '2,"Imael Angel","BAD TIMES"\n'
)


def test_the_preamble_is_skipped_and_every_row_is_read() -> None:
    tracks = parse_chart_csv(_CHART_CSV)

    assert [track.model_dump() for track in tracks] == [
        {"rank": 1, "artist": "HUGEL, Imael Angel & Ultra Naté", "title": "Movin' To The Sun"},
        {"rank": 2, "artist": "Imael Angel", "title": "BAD TIMES"},
    ]


def test_a_body_without_the_header_is_rejected() -> None:
    with pytest.raises(BadParseData):
        parse_chart_csv("<!doctype html>\n")


@pytest.mark.asyncio
async def test_the_world_chart_carries_two_hundred_ranked_entries() -> None:
    tracks = await Shazam().top_world_tracks()

    assert len(tracks) == 200
    assert [track.rank for track in tracks[:3]] == [1, 2, 3]


@pytest.mark.asyncio
async def test_a_city_chart_resolves_its_country_and_city_slugs() -> None:
    tracks = await Shazam().top_city_tracks(
        country_code="RU",
        city_name="Moscow",
        limit=5,
    )

    assert [track.rank for track in tracks] == [1, 2, 3, 4, 5]


# Parametrized rather than sampled: a genre Shazam renames stops having a chart
#  and answers `404`, which is how `regional-mexicano` left the enum.
@pytest.mark.asyncio
@pytest.mark.parametrize(
    "genre",
    [pytest.param(genre, id=genre.value) for genre in GenreMusic],
)
async def test_a_world_genre_chart_answers_for_every_genre_the_enum_carries(
    genre: GenreMusic,
) -> None:
    tracks = await Shazam().top_world_genre_tracks(
        genre=genre,
        limit=5,
    )

    assert [track.rank for track in tracks] == [1, 2, 3, 4, 5]
