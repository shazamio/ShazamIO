import csv
import io
from typing import Final

from shazamio.exceptions import BadParseData
from shazamio.loggers import main as logger
from shazamio.schemas.charts import ChartTrack

__all__ = [
    "CHART_CONTENT_TYPE",
    "parse_chart_csv",
]

CHART_CONTENT_TYPE: Final[str] = "text/csv"

# The body opens with a byte order mark, a blank line and a quoted caption
#  ("Monday, 14 September 2026 [performance over the past 7 days]"), so the
#  header row is the only place the rows can be keyed off.
_HEADER: Final[list[str]] = ["Rank", "Artist", "Title"]


def parse_chart_csv(payload: str) -> list[ChartTrack]:
    rows = csv.reader(io.StringIO(payload))

    for row in rows:
        if row == _HEADER:
            break
    else:
        msg = f"Chart CSV carries no {','.join(_HEADER)} header"
        raise BadParseData(msg)

    tracks: list[ChartTrack] = []
    for row in rows:
        # One `film-tv-and-stage` row came with four fields and failed the whole chart:
        #  `ValueError: too many values to unpack (expected 3, got 4)`.
        #  https://github.com/shazamio/ShazamIO/actions/runs/41474411738
        if len(row) != len(_HEADER):
            logger.warning(
                "parse_chart_csv.skip",
                extra={"row": row},
            )
            continue

        rank, artist, title = row
        track = ChartTrack(
            rank=int(rank),
            artist=artist,
            title=title,
        )
        tracks.append(track)

    return tracks
