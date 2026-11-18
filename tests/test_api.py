from collections.abc import Awaitable
from pathlib import Path
from typing import Any, Final, Protocol

import pytest
from pydantic import BaseModel

from shazamio import BadParseData, Shazam

_GLORIA: Final[Path] = Path(__file__).parents[1] / "examples" / "data" / "Gloria.ogg"
# A section `type` the discriminated union does not know, so no model accepts the answer.
_UNKNOWN_SECTION: Final[dict[str, Any]] = {
    "key": "1",
    "title": "t",
    "subtitle": "s",
    "sections": [{"type": "MUSIC_VIDEO", "tabname": "Video"}],
}


class _Lookup(Protocol):
    def __call__(self, shazam: Shazam) -> Awaitable[BaseModel]:
        """Ask `shazam` for one answer."""


async def _track_about(shazam: Shazam) -> BaseModel:
    return await shazam.track_about(track_id=1)


async def _youtube(shazam: Shazam) -> BaseModel:
    return await shazam.get_youtube_data(link="https://video.example/youtube")


async def _recognize(shazam: Shazam) -> BaseModel:
    return await shazam.recognize(_GLORIA)


@pytest.mark.parametrize(
    ("lookup", "payload"),
    [
        pytest.param(_track_about, _UNKNOWN_SECTION, id="track-about"),
        pytest.param(_youtube, {"caption": "c"}, id="youtube"),
        pytest.param(_recognize, {"tagid": "x", "track": _UNKNOWN_SECTION}, id="recognize"),
    ],
)
async def test_an_answer_the_model_rejects_raises_bad_parse_data(
    shazam: Shazam,
    monkeypatch: pytest.MonkeyPatch,
    *,
    lookup: _Lookup,
    payload: dict[str, Any],
) -> None:
    async def request(
        method: str,
        url: str,
        /,
        *,
        headers: dict[str, str],
        proxy: str | None,
        json: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        del method, url, headers, proxy, json  # The answer is fixed; nothing is sent.
        return payload

    monkeypatch.setattr(shazam.http_client, "request", request)

    with pytest.raises(BadParseData, match="Shazam answer is not a"):
        await lookup(shazam)
