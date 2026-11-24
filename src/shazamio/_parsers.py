import csv
import io
import logging
from typing import Final, TypeVar

from pydantic import BaseModel, Field, TypeAdapter, ValidationError

from shazamio.exceptions import BadPayload, NotFound
from shazamio.models import ChartTrack

__all__ = [
    "Locations",
    "SearchAnswer",
    "parse_apple_ids",
    "parse_chart",
    "parse_model",
]

logger = logging.getLogger(name=__name__)

# The body opens with a byte order mark, a blank line and a quoted caption
#  ("Monday, 14 September 2026 [performance over the past 7 days]"), so the
#  header row is the only place the rows can be keyed off.
_CHART_HEADER: Final[list[str]] = ["Rank", "Artist", "Title"]

# PEP 695 generics need Python 3.12, and the package supports 3.11.
_Model = TypeVar("_Model", bound=BaseModel)


class _City(BaseModel):
    name: str
    url_name: str = Field(alias="urlName")


class _Country(BaseModel):
    code: str = Field(alias="id")
    url_name: str = Field(alias="urlName")
    cities: list[_City]


class Locations(BaseModel):
    countries: list[_Country]


class _Song(BaseModel):
    track_id: int = Field(alias="trackId")


class SearchAnswer(BaseModel):
    results: list[_Song]


# A storefront the service does not serve and ids it cannot resolve are both
#  `200 {"error":{"msg":"Could not fetch ids"}}`, so the body decides and the
#  status says nothing.
class _AppleIdsError(BaseModel):
    error: dict[str, str]


_APPLE_IDS: Final[TypeAdapter[_AppleIdsError | dict[str, str]]] = TypeAdapter(
    _AppleIdsError | dict[str, str],
)


def parse_model(
    payload: str,
    *,
    model: type[_Model],
) -> _Model:
    try:
        return model.model_validate_json(payload)
    except ValidationError as er:
        msg = f"The answer is not a `{model.__name__}`: {payload[:200]}"
        raise BadPayload(msg) from er


def parse_chart(payload: str) -> list[ChartTrack]:
    rows = csv.reader(io.StringIO(payload))

    for row in rows:
        if row == _CHART_HEADER:
            break
    else:
        msg = f"Chart CSV carries no {','.join(_CHART_HEADER)} header"
        raise BadPayload(msg)

    tracks: list[ChartTrack] = []
    for row in rows:
        # One `film-tv-and-stage` row came with four fields and failed the whole chart:
        #  `ValueError: too many values to unpack (expected 3, got 4)`.
        #  https://github.com/shazamio/ShazamIO/actions/runs/41474411738
        if len(row) != len(_CHART_HEADER):
            logging_extra = {"row": row}
            logger.warning("parse_chart.skip", extra=logging_extra)
            continue

        rank, artist, title = row
        track = ChartTrack(
            rank=int(rank),
            artist=artist,
            title=title,
        )
        tracks.append(track)

    return tracks


def parse_apple_ids(payload: str) -> dict[str, str]:
    try:
        answer = _APPLE_IDS.validate_json(payload)
    except ValidationError as er:
        msg = f"Apple id mapping is not a map of ids to keys: {payload[:200]}"
        raise BadPayload(msg) from er

    if isinstance(answer, _AppleIdsError):
        msg = f"Apple ids could not be resolved: {answer.error}"
        raise NotFound(msg)

    return answer
