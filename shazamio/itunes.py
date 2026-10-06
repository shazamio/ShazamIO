from typing import Final

from pydantic import BaseModel, Field, ValidationError

from shazamio.exceptions import BadParseData

# The search answers JSON as `text/javascript`, so `response.json()` raises
#  `ContentTypeError` and the body is decoded by hand:
#  `curl -sI 'https://itunes.apple.com/search?term=adele&entity=song&limit=1'`.
ITUNES_SEARCH_CONTENT_TYPE: Final[str] = "text/javascript"
# Apple serves `limit` from 1 to 200 (https://performance-partners.apple.com/search-api)
#  and answers `0` or a negative one with 20 songs, not with an error.
ITUNES_SEARCH_MAX_LIMIT: Final[int] = 200


class _Song(BaseModel):
    track_id: int = Field(alias="trackId")


class _SearchAnswer(BaseModel):
    results: list[_Song]


def parse_itunes_track_ids(payload: str) -> list[int]:
    try:
        answer = _SearchAnswer.model_validate_json(payload)
    except ValidationError as er:
        msg = f"iTunes search answer carries no track ids: {payload[:200]}"
        raise BadParseData(msg) from er

    return [song.track_id for song in answer.results]
