import csv
import io
from typing import Final

from shazamio.exceptions import BadParseData
from shazamio.schemas.charts import ChartTrack

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

    return [
        ChartTrack(
            rank=int(rank),
            artist=artist,
            title=title,
        )
        for rank, artist, title in rows
    ]
