from pathlib import Path
from typing import Any, Final

import pytest

from shazamio import Serialize, Shazam

_GLORIA: Final[Path] = Path(__file__).parents[1] / "examples" / "data" / "Gloria.ogg"
_LINK: Final[str] = "https://video.example/youtube/video?q=x"
_PROXY: Final[str] = "http://proxy.example:8080"
_HEADERS: Final[dict[str, str]] = {"X-Shazam-Platform": "IPHONE"}


@pytest.mark.asyncio
async def test_the_lookup_sends_the_shazam_headers_through_the_proxy(
    shazam: Shazam,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    sent: list[dict[str, Any]] = []

    async def request(
        method: str,
        url: str,
        /,
        *,
        headers: dict[str, str],
        proxy: str | None,
    ) -> dict[str, Any]:
        sent.append({"method": method, "url": url, "headers": headers, "proxy": proxy})
        return {}

    monkeypatch.setattr(shazam, "headers", lambda: _HEADERS)
    monkeypatch.setattr(shazam.http_client, "request", request)

    await shazam.get_youtube_data(
        link=_LINK,
        proxy=_PROXY,
    )

    assert sent == [{"method": "GET", "url": _LINK, "headers": _HEADERS, "proxy": _PROXY}]


@pytest.mark.vcr
@pytest.mark.asyncio
async def test_a_recognized_track_leads_to_its_youtube_video(shazam: Shazam) -> None:
    track = Serialize.full_track(await shazam.recognize(data=_GLORIA)).track
    assert track is not None
    assert track.youtube_link is not None

    video = Serialize.youtube(await shazam.get_youtube_data(link=track.youtube_link))

    assert video.model_dump() == {
        "caption": "Gloria Gaynor - I Will Survive",
        "image": {
            "dimensions": {"width": 1280, "height": 720},
            "url": "https://i.ytimg.com/vi/6dYWe1c3OyU/maxresdefault.jpg",
        },
        "actions": [
            {
                "name": "video:youtube",
                "type": "webview",
                "uri": "https://youtu.be/6dYWe1c3OyU?autoplay=1",
            },
        ],
        "uri": "https://youtu.be/6dYWe1c3OyU?autoplay=1",
    }
