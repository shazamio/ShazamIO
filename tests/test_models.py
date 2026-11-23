from http import HTTPStatus
from typing import Any, Final
from uuid import UUID

import pytest
from aiohttp import ClientSession

from shazamio import ResponseTrack, Shazam, TrackInfo, YoutubeData
from shazamio._requests import headers

# The shape Shazam's list endpoints return for a track that has no Spotify
#  provider: `hub.providers` is absent, so every field mapped onto a path
#  through it must fall back to its default instead of failing the load.
_TRACK_WITHOUT_SPOTIFY_PROVIDER: Final[dict[str, Any]] = {
    "key": "47440537",
    "title": "Arrival To Earth",
    "subtitle": "Steve Jablonsky",
    "images": {"coverarthq": "https://images.example/cover.jpg"},
    "hub": {"actions": [{"uri": "a"}, {"uri": "ringtone://example"}]},
    # Both artist ids, as Shazam serves them; `TrackInfo.artist_id` says which counts.
    "artists": [{"id": "42", "adamid": "21402948"}],
}


# The URL Shazam's own `VIDEO` section carried for this track.
_ARRIVAL_TO_EARTH_VIDEO: Final[str] = (
    "https://cdn.shazam.com/video/v3/-/GB/iphone/47440537/youtube"
    "/video?q=Steve+Jablonsky+%22Arrival+To+Earth%22"
)


# What a recognition that matched nothing answers. Measured live on
#  `examples/data/dora.ogg`, whose whole payload is these three keys: `retryms`
#  is Shazam saying how long to record before asking again, and it is the only
#  thing that separates a clip absent from the index from one that was too short.
_NO_MATCH: Final[dict[str, Any]] = {
    "tagid": "11111111-1111-7111-8111-111111111111",
    "retryms": 7000,
    "matches": [],
}

_VIDEO_WITHOUT_ACTIONS: Final[dict[str, Any]] = {
    "caption": "c",
    "image": {"dimensions": {"width": 1, "height": 1}, "url": "https://image.example"},
    "actions": [],
}

# Keys no field reads, which a caller of the dict results could read before.
_UNMODELED: Final[dict[str, Any]] = {"genres": {"primary": "Soundtrack"}, "isrc": "USA2P0700146"}
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
_LIVE_TRACK_ID: Final[int] = 53982678
# The id the field used to be built from, and a key Shazam has no track for.
_URL_OF_A_DEAD_KEY: Final[str] = "https://www.shazam.com/track/42"
_SONG_ROUTE: Final[str] = "/song/"


def test_track_missing_paths_fall_back_to_defaults() -> None:
    track = TrackInfo.model_validate(_TRACK_WITHOUT_SPOTIFY_PROVIDER)

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
        "youtube_link": _ARRIVAL_TO_EARTH_VIDEO,
        "sections": [],
    }


def test_sections_resolve_by_type_discriminator() -> None:
    track = TrackInfo.model_validate(
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


def test_a_video_section_wins_over_the_rebuilt_link() -> None:
    track = TrackInfo.model_validate(
        {
            "key": "1",
            "title": "t",
            "subtitle": "s",
            "sections": [{"type": "VIDEO", "tabname": "Video", "youtubeurl": "https://youtu.be/x"}],
        },
    )

    assert track.youtube_link == "https://youtu.be/x"


def test_a_video_without_actions_has_no_uri() -> None:
    video = YoutubeData.model_validate(_VIDEO_WITHOUT_ACTIONS)

    assert video.uri is None


def test_the_spotify_fields_read_the_spotify_provider() -> None:
    track = TrackInfo.model_validate(_TRACK_WITH_PROVIDERS)

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
        "youtube_link": _ARRIVAL_TO_EARTH_VIDEO,
        "sections": [],
    }


async def _status(
    session: ClientSession,
    *,
    url: str,
) -> int:
    async with session.get(url, allow_redirects=False) as response:
        return response.status


async def _redirect_target(
    session: ClientSession,
    *,
    url: str,
) -> str:
    async with session.get(url, allow_redirects=False) as response:
        return response.headers.get("Location", "")


# The redirect is gated on the Shazam headers: with a browser `User-Agent` the
#  site answers `200` and its 1.7MB shell for every `/track/` path, dead keys
#  included, so a probe without them cannot tell a live page from a missing one.
#  It is gated on the address too, so the dead key is the probe for whether the
#  route is served here at all, and not only the control for the live half.
@pytest.mark.vcr
@pytest.mark.asyncio
async def test_the_built_url_resolves_and_a_dead_key_does_not(shazam: Shazam) -> None:
    track = await shazam.track_about(track_id=_LIVE_TRACK_ID)

    assert track.shazam_url == f"https://www.shazam.com/track/{_LIVE_TRACK_ID}"

    async with ClientSession(headers=headers("en-US")) as session:
        dead_status = await _status(session, url=_URL_OF_A_DEAD_KEY)
        target = await _redirect_target(session, url=track.shazam_url)

    if dead_status != HTTPStatus.NOT_FOUND:
        reason: str = f"`/track/` is not served to this address: a dead key answers {dead_status}"
        pytest.skip(reason)

    # Matched, not anchored: what the claim needs is the song route, whatever the
    #  site puts in front of it.
    assert _SONG_ROUTE in target, f"dead key: {dead_status}, live key: {target!r}"


def test_a_result_that_matched_nothing_carries_the_retry_hint() -> None:
    answer = ResponseTrack.model_validate(_NO_MATCH)

    assert answer.model_dump() == {
        "tag_id": UUID("11111111-1111-7111-8111-111111111111"),
        "retry_ms": 7000,
        "location": None,
        "matches": [],
        "timestamp": None,
        "timezone": None,
        "track": None,
    }


def test_keys_no_field_reads_stay_on_the_model() -> None:
    track = TrackInfo.model_validate(_TRACK_WITHOUT_SPOTIFY_PROVIDER | _UNMODELED)
    answer = ResponseTrack.model_validate(_NO_MATCH | _UNMODELED)
    video = YoutubeData.model_validate(_VIDEO_WITHOUT_ACTIONS | _UNMODELED)

    assert [track.model_extra, answer.model_extra, video.model_extra] == [_UNMODELED] * 3


@pytest.fixture(scope="session")
def song_response() -> dict[str, Any]:
    return {
        "matches": [
            {
                "id": "230272433",
                "offset": 187.4215,
                "timeskew": -0.0001565814,
                "frequencyskew": -0.000080525875,
            },
        ],
        "location": {"accuracy": 0.01},
        "timestamp": 1652380596486,
        "timezone": "Europe/Moscow",
        "track": {
            "layout": "5",
            "type": "MUSIC",
            "key": "47440537",
            "title": "Arrival To Earth",
            "subtitle": "Steve Jablonsky",
            "images": {
                "background": "https://is3-ssl.mzstatic.com/image/thumb/Features125/v4/c2/35/67"
                "/c23567d0-0f59-8573-5848-0a7844ed3416/mzl.fxlsnewc.jpg/800x800cc"
                ".jpg",
                "coverart": "https://is2-ssl.mzstatic.com/image/thumb/Music/c8/a6/4a/mzi.akybahch"
                ".jpg/400x400cc.jpg",
                "coverarthq": "https://is2-ssl.mzstatic.com/image/thumb/Music/c8/a6/4a/mzi"
                ".akybahch.jpg/400x400cc.jpg",
                "joecolor": "b:010417p:aec4d5s:ef9b41t:8c9dafq:bf7c38",
            },
            "share": {
                "subject": "Arrival To Earth - Steve Jablonsky",
                "text": "I used Shazam to discover Arrival To Earth by Steve Jablonsky.",
                "href": "https://www.shazam.com/track/47440537/arrival-to-earth",
                "image": "https://is2-ssl.mzstatic.com/image/thumb/Music/c8/a6/4a/mzi.akybahch"
                ".jpg/400x400cc.jpg",
                "twitter": "I used @Shazam to discover Arrival To Earth by Steve Jablonsky.",
                "html": "https://www.shazam.com/snippets/email-share/47440537?lang=en&country=GB",
                "avatar": "https://is3-ssl.mzstatic.com/image/thumb/Features125/v4/c2/35/67"
                "/c23567d0-0f59-8573-5848-0a7844ed3416/mzl.fxlsnewc.jpg/800x800cc.jpg",
                "snapchat": "https://www.shazam.com/partner/sc/track/47440537",
            },
            "hub": {
                "type": "APPLEMUSIC",
                "image": "https://images.shazam.com/static/icons/hub/ios/v5/applemusic_{"
                "scalefactor}.png",
                "actions": [
                    {"name": "apple", "type": "applemusicplay", "id": "265018693"},
                    {
                        "name": "apple",
                        "type": "uri",
                        "uri": "https://audio-ssl.itunes.apple.com/itunes-assets/AudioPreview125"
                        "/v4/9c/1d/ec/9c1dec79-214a-c3a4-846b-87787421dc33"
                        "/mzaf_5388156565692493963.plus.aac.ep.m4a",
                    },
                ],
                "options": [
                    {
                        "caption": "OPEN IN",
                        "actions": [
                            {
                                "name": "hub:applemusic:deeplink",
                                "type": "applemusicopen",
                                "uri": "https://music.apple.com/gb/album/arrival-to-earth/265018176"
                                "?i=265018693&mttnagencyid=s2n&mttnsiteid=125115&mttn3pid"
                                "=Apple-Shazam&mttnsub1=Shazam_ios&mttnsub2=5348615A-616D"
                                "-3235-3830-44754D6D5973&itscg=30201&app=music&itsct=Shazam_ios",
                            },
                            {
                                "name": "hub:applemusic:deeplink",
                                "type": "uri",
                                "uri": "https://music.apple.com/gb/album/arrival-to-earth/265018176"
                                "?i=265018693&mttnagencyid=s2n&mttnsiteid=125115&mttn3pid"
                                "=Apple-Shazam&mttnsub1=Shazam_ios&mttnsub2=5348615A-616D"
                                "-3235-3830-44754D6D5973&itscg=30201&app=music&itsct=Shazam_ios",
                            },
                        ],
                        "beacondata": {"type": "open", "providername": "applemusic"},
                        "image": "https://images.shazam.com/static/icons/hub/ios/v5/overflow-open"
                        "-option_{scalefactor}.png",
                        "type": "open",
                        "listcaption": "Open in Apple Music",
                        "overflowimage": "https://images.shazam.com/static/icons/hub/ios/v5/applemusic"
                        "-overflow_{scalefactor}.png",
                        "colouroverflowimage": False,
                        "providername": "applemusic",
                    },
                    {
                        "caption": "BUY",
                        "actions": [
                            {
                                "type": "uri",
                                "uri": "https://itunes.apple.com/gb/album/arrival-to-earth/265018176"
                                "?i=265018693&mttnagencyid=s2n&mttnsiteid=125115&mttn3pid"
                                "=Apple-Shazam&mttnsub1=Shazam_ios&mttnsub2=5348615A-616D"
                                "-3235-3830-44754D6D5973&itscg=30201&app=itunes&itsct=Shazam_ios",
                            },
                        ],
                        "beacondata": {"type": "buy", "providername": "itunes"},
                        "image": "https://images.shazam.com/static/icons/hub/ios/v5/itunes"
                        "-overflow-buy_{scalefactor}.png",
                        "type": "buy",
                        "listcaption": "Buy on iTunes",
                        "overflowimage": "https://images.shazam.com/static/icons/hub/ios/v5/itunes-overflow"
                        "-buy_{scalefactor}.png",
                        "colouroverflowimage": False,
                        "providername": "itunes",
                    },
                ],
                "providers": [
                    {
                        "caption": "Open in Spotify",
                        "images": {
                            "overflow": "https://images.shazam.com/static/icons/hub/ios/v5/spotify"
                            "-overflow_{scalefactor}.png",
                            "default": "https://images.shazam.com/static/icons/hub/ios/v5/spotify_{"
                            "scalefactor}.png",
                        },
                        "actions": [
                            {
                                "name": "hub:spotify:searchdeeplink",
                                "type": "uri",
                                "uri": "spotify:search:Arrival%20To%20Earth%20Steve%20Jablonsky",
                            },
                        ],
                        "type": "SPOTIFY",
                    },
                    {
                        "caption": "Open in Deezer",
                        "images": {
                            "overflow": "https://images.shazam.com/static/icons/hub/ios/v5/deezer"
                            "-overflow_{scalefactor}.png",
                            "default": "https://images.shazam.com/static/icons/hub/ios/v5/deezer_{"
                            "scalefactor}.png",
                        },
                        "actions": [
                            {
                                "name": "hub:deezer:searchdeeplink",
                                "type": "uri",
                                "uri": "deezer-query://www.deezer.com/play?query=%7Btrack%3A"
                                "%27Arrival+To+Earth%27%20artist%3A%27Steve+Jablonsky%27%7D ",
                            },
                        ],
                        "type": "DEEZER",
                    },
                ],
                "explicit": False,
                "displayname": "APPLE MUSIC",
            },
            "sections": [
                {
                    "type": "SONG",
                    "metapages": [
                        {
                            "image": "https://is3-ssl.mzstatic.com/image/thumb/Features125/v4/c2"
                            "/35/67/c23567d0-0f59-8573-5848-0a7844ed3416/mzl.fxlsnewc"
                            ".jpg/800x800cc.jpg",
                            "caption": "Steve Jablonsky",
                        },
                        {
                            "image": "https://is2-ssl.mzstatic.com/image/thumb/Music/c8/a6/4a/mzi"
                            ".akybahch.jpg/400x400cc.jpg",
                            "caption": "Arrival To Earth",
                        },
                    ],
                    "tabname": "Song",
                    "metadata": [
                        {"title": "Album", "text": "Transformers: The Score"},
                        {"title": "Label", "text": "Warner Records"},
                        {"title": "Released", "text": "2007"},
                    ],
                },
                {
                    "type": "VIDEO",
                    "tabname": "Video",
                    "youtubeurl": "https://cdn.shazam.com/video/v3/-/GB/iphone/47440537/youtube"
                    "/video?q=Steve+Jablonsky+%22Arrival+To+Earth%22",
                },
                {
                    "type": "ARTIST",
                    "avatar": "https://is3-ssl.mzstatic.com/image/thumb/Features125/v4/c2/35/67"
                    "/c23567d0-0f59-8573-5848-0a7844ed3416/mzl.fxlsnewc.jpg/800x800cc"
                    ".jpg",
                    "id": "10194644",
                    "name": "Steve Jablonsky",
                    "verified": False,
                    "url": "https://cdn.shazam.com/digest/v1/en/GB/iphone/artist/10194644"
                    "/recentpost",
                    "actions": [
                        {"type": "artistposts", "id": "10194644"},
                        {"type": "artist", "id": "10194644"},
                    ],
                    "tabname": "Artist",
                    "toptracks": {
                        "url": "https://cdn.shazam.com/shazam/v3/en/GB/iphone/-/tracks"
                        "/artisttoptracks_10194644?startFrom=0&pageSize=20&connected=",
                    },
                },
                {
                    "type": "RELATED",
                    "url": "https://cdn.shazam.com/shazam/v3/en/GB/iphone/-/tracks/track"
                    "-similarities-id-47440537?startFrom=0&pageSize=20&connected=",
                    "tabname": "Related",
                },
            ],
            "url": "https://www.shazam.com/track/47440537/arrival-to-earth",
            "artists": [{"id": "10194644", "adamid": "21402948"}],
            "isrc": "USWB10703613",
            "genres": {"primary": "Soundtrack"},
            "urlparams": {
                "{tracktitle}": "Arrival+To+Earth",
                "{trackartist}": "Steve+Jablonsky",
            },
            "myshazam": {
                "apple": {
                    "actions": [
                        {
                            "name": "myshazam:apple",
                            "type": "uri",
                            "uri": "https://music.apple.com/gb/album/arrival-to-earth/265018176?i"
                            "=265018693&mttnagencyid=s2n&mttnsiteid=125115&mttn3pid=Apple"
                            "-Shazam&mttnsub1=Shazam_ios&mttnsub2=5348615A-616D-3235-3830"
                            "-44754D6D5973&itscg=30201&app=music&itsct=Shazam_ios",
                        },
                    ],
                },
            },
            "highlightsurls": {
                "artisthighlightsurl": "https://cdn.shazam.com/video/v3/en/GB/iphone/21402948/highlights?affiliate"
                "=mttnagencyid%3Ds2n%26mttnsiteid%3D125115%26mttn3pid%3DApple-Shazam"
                "%26mttnsub1%3DShazam_ios%26mttnsub2%3D5348615A-616D-3235-3830-44754D6D5973"
                "%26itscg%3D30201%26app%3Dmusic%26itsct%3DShazam_ios",
                "relatedhighlightsurl": "https://cdn.shazam.com/video/v3/en/GB/iphone/10194644/artist-similarities-id"
                "-10194644/relatedhighlights?max_artists=5&affiliate=mttnagencyid%3Ds2n"
                "%26mttnsiteid%3D125115%26mttn3pid%3DApple-Shazam%26mttnsub1%3DShazam_ios"
                "%26mttnsub2%3D5348615A-616D-3235-3830-44754D6D5973%26itscg%3D30201%26app"
                "%3Dmusic%26itsct%3DShazam_ios",
            },
            "relatedtracksurl": "https://cdn.shazam.com/shazam/v3/en/GB/iphone/-/tracks/track"
            "-similarities-id-47440537?startFrom=0&pageSize=20&connected=",
            "albumadamid": "265018176",
        },
        "tagid": "89A4C33B-58C6-4A50-8475-94032FC34D06",
    }


@pytest.mark.asyncio
async def test_recognize_song_bug(song_response: dict[str, Any]) -> None:
    serialize_out = ResponseTrack.model_validate(song_response)
    assert serialize_out.matches[0].channel is None
