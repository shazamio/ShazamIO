from http import HTTPStatus
from typing import Any, Final
from uuid import UUID

import pytest
from aiohttp import ClientSession

from shazamio import Serialize, Shazam

# The shape Shazam's list endpoints return for a track that has no Spotify
#  provider: `hub.providers` is absent, so every field mapped onto a path
#  through it must fall back to its default instead of failing the load.
_TRACK_WITHOUT_SPOTIFY_PROVIDER: Final[dict[str, Any]] = {
    "key": "47440537",
    "title": "Arrival To Earth",
    "subtitle": "Steve Jablonsky",
    "images": {"coverarthq": "https://images.example/cover.jpg"},
    "hub": {"actions": [{"uri": "a"}, {"uri": "ringtone://example"}]},
    # Both artist ids, as Shazam serves them: `id` is the literal `42` on every
    #  payload, `adamid` is the one that identifies the artist.
    "artists": [{"id": "42", "adamid": "21402948"}],
}


# What a recognition that matched nothing answers. Measured live on
#  `examples/data/dora.ogg`, whose whole payload is these three keys: `retryms`
#  is Shazam saying how long to record before asking again, and it is the only
#  thing that separates a clip absent from the index from one that was too short.
_NO_MATCH: Final[dict[str, Any]] = {
    "tagid": "11111111-1111-7111-8111-111111111111",
    "retryms": 7000,
    "matches": [],
}


def test_track_missing_paths_fall_back_to_defaults() -> None:
    track = Serialize.track(_TRACK_WITHOUT_SPOTIFY_PROVIDER)

    assert track.model_dump() == {
        "key": 47440537,
        "title": "Arrival To Earth",
        "subtitle": "Steve Jablonsky",
        "artist_id": "21402948",
        "shazam_url": "https://www.shazam.com/track/47440537",
        "photo_url": "https://images.example/cover.jpg",
        "spotify_uri_query": None,
        "apple_music_url": None,
        "ringtone": "ringtone://example",
        "providers": [],
        "spotify_uri": None,
        "youtube_link": None,
        "sections": [],
    }


def test_sections_resolve_by_type_discriminator() -> None:
    track = Serialize.track(
        {
            "key": "1",
            "title": "t",
            "subtitle": "s",
            "sections": [
                {"type": "SONG", "metapages": [], "tabname": "Song", "metadata": []},
                {"type": "VIDEO", "tabname": "Video", "youtubeurl": "https://youtu.be/x"},
                # The ARTIST entry is the case the discriminator exists for:
                #  structurally it also matches `RelatedSection`.
                {
                    "type": "ARTIST",
                    "id": "10194644",
                    "name": "Steve Jablonsky",
                    "verified": False,
                    "url": "https://related-lookalike.example",
                    "actions": [{"type": "artist", "id": "10194644"}],
                    "tabname": "Artist",
                    "toptracks": {"url": "https://tracks.example/top"},
                },
                {"type": "RELATED", "url": "https://related.example", "tabname": "Related"},
            ],
        },
    )

    section_types = [type(section).__name__ for section in track.sections]
    assert section_types == ["SongSection", "VideoSection", "ArtistSection", "RelatedSection"]


# The shape the `iphone` profile returns: one action per provider, so a mapping
#  onto `actions[1]` reads nothing and leaves the Spotify fields `None`.
_TRACK_WITH_PROVIDERS: Final[dict[str, Any]] = {
    "key": "47440537",
    "title": "Arrival To Earth",
    "subtitle": "Steve Jablonsky",
    "hub": {
        "providers": [
            {
                "caption": "Open in Spotify",
                "type": "SPOTIFY",
                "actions": [
                    {
                        "name": "hub:spotify:searchdeeplink",
                        "type": "uri",
                        "uri": "spotify:search:Arrival%20To%20Earth%20Steve%20Jablonsky",
                    },
                ],
            },
            {
                "caption": "Open in Deezer",
                "type": "DEEZER",
                "actions": [
                    {
                        "name": "hub:deezer:searchdeeplink",
                        "type": "uri",
                        "uri": "deezer-query://www.deezer.com/play?query=x",
                    },
                ],
            },
        ],
    },
}


def test_the_spotify_fields_read_the_spotify_provider() -> None:
    track = Serialize.track(_TRACK_WITH_PROVIDERS)

    assert track.model_dump() == {
        "key": 47440537,
        "title": "Arrival To Earth",
        "subtitle": "Steve Jablonsky",
        "artist_id": None,
        "shazam_url": "https://www.shazam.com/track/47440537",
        "photo_url": None,
        "spotify_uri_query": "Arrival%20To%20Earth%20Steve%20Jablonsky",
        "apple_music_url": None,
        "ringtone": None,
        "providers": [
            {
                "caption": "Open in Spotify",
                "type": "SPOTIFY",
                "actions": [
                    {
                        "name": "hub:spotify:searchdeeplink",
                        "type": "uri",
                        "uri": "spotify:search:Arrival%20To%20Earth%20Steve%20Jablonsky",
                    },
                ],
            },
            {
                "caption": "Open in Deezer",
                "type": "DEEZER",
                "actions": [
                    {
                        "name": "hub:deezer:searchdeeplink",
                        "type": "uri",
                        "uri": "deezer-query://www.deezer.com/play?query=x",
                    },
                ],
            },
        ],
        "spotify_uri": "spotify:search:Arrival%20To%20Earth%20Steve%20Jablonsky",
        "youtube_link": None,
        "sections": [],
    }


_LIVE_TRACK_ID: Final[int] = 53982678
# The id the field used to be built from, and a key Shazam has no track for.
_URL_OF_A_DEAD_KEY: Final[str] = "https://www.shazam.com/track/42"
_SONG_ROUTE: Final[str] = "/song/"


async def _status(session: ClientSession, *, url: str) -> int:
    async with session.get(url, allow_redirects=False) as response:
        return response.status


async def _redirect_target(session: ClientSession, *, url: str) -> str:
    async with session.get(url, allow_redirects=False) as response:
        return response.headers.get("Location", "")


# The redirect is gated on the Shazam headers: with a browser `User-Agent` the
#  site answers `200` and its 1.7MB shell for every `/track/` path, dead keys
#  included, so a probe without them cannot tell a live page from a missing one.
#  It is gated on the address too, so the dead key is the probe for whether the
#  route is served here at all, and not only the control for the live half.
@pytest.mark.asyncio
async def test_the_built_url_resolves_and_a_dead_key_does_not() -> None:
    shazam = Shazam()
    track = Serialize.track(await shazam.track_about(track_id=_LIVE_TRACK_ID))

    assert track.shazam_url == f"https://www.shazam.com/track/{_LIVE_TRACK_ID}"

    async with ClientSession(headers=shazam.headers()) as session:
        dead_status = await _status(session, url=_URL_OF_A_DEAD_KEY)
        target = await _redirect_target(session, url=track.shazam_url)

    if dead_status != HTTPStatus.NOT_FOUND:
        reason: str = f"`/track/` is not served to this address: a dead key answers {dead_status}"
        pytest.skip(reason)

    # Matched, not anchored: what the claim needs is the song route, whatever the
    #  site puts in front of it.
    assert _SONG_ROUTE in target, f"dead key: {dead_status}, live key: {target!r}"


def test_a_result_that_matched_nothing_carries_the_retry_hint() -> None:
    answer = Serialize.full_track(_NO_MATCH)

    assert answer.model_dump() == {
        "tag_id": UUID("11111111-1111-7111-8111-111111111111"),
        "retry_ms": 7000,
        "location": None,
        "matches": [],
        "timestamp": None,
        "timezone": None,
        "track": None,
    }
