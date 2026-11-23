import asyncio
import json
import re
import warnings
from http import HTTPStatus
from pathlib import Path
from typing import Any, Final, Protocol

import pytest
from shazamio_core import Signature, SignatureError

from shazamio import (
    BadPayload,
    BadResponse,
    Device,
    GenreMusic,
    NotFound,
    RateLimited,
    Request,
    Response,
    ResponseTrack,
    SearchParams,
    Shazam,
    TrackInfo,
)
from shazamio import _service as service
from shazamio.testing import MockTransport

# Anchored to this file, so the suite runs from any working directory.
_GLORIA: Final[Path] = Path(__file__).parents[1] / "examples" / "data" / "Gloria.ogg"
_TAG_ID: Final[str] = "0B9D4C34-6D3A-4F0B-9A4E-2B1C8E7F6A51"
_NO_MATCH: Final[ResponseTrack] = ResponseTrack.model_validate({"matches": [], "tagid": _TAG_ID})
_UUID: Final[re.Pattern[str]] = re.compile(r"[0-9A-F]{8}(?:-[0-9A-F]{4}){3}-[0-9A-F]{12}")
_HEADERS: Final[dict[str, str]] = {"X-Shazam-Platform": "IPHONE"}
_CSV: Final[str] = service.CHART_CONTENT_TYPE
_JSON: Final[str] = service.JSON_CONTENT_TYPE
_ROUTE: Final[str] = "https://amp.shazam.com/discovery/v5/en-US/GB"
_GLORIA_TRACK: Final[str] = json.dumps(
    {"key": "53982678", "title": "I Will Survive", "subtitle": "Gloria Gaynor"},
)
# A section `type` the discriminated union does not know, so no model accepts the answer.
_UNKNOWN_SECTION: Final[dict[str, Any]] = {
    "key": "1",
    "title": "t",
    "subtitle": "s",
    "sections": [{"type": "MUSIC_VIDEO", "tabname": "Video"}],
}
_LINK: Final[str] = "https://video.example/youtube/video?q=x"
_VIDEO: Final[str] = json.dumps(
    {
        "caption": "",
        "image": {"dimensions": {"width": 0, "height": 0}, "url": ""},
        "actions": [],
    },
)
# A city name shared by two countries, listed in the other country first, not
#  first among its own country's cities, and listed twice there, so only the
#  first match is the right one.
_LOCATIONS: Final[str] = json.dumps(
    {
        "countries": [
            {
                "id": "BY",
                "urlName": "belarus",
                "cities": [{"name": "Moscow", "urlName": "moscow-by"}],
            },
            {
                "id": "RU",
                "urlName": "russia",
                "cities": [
                    {"name": "Kazan", "urlName": "kazan"},
                    {"name": "Moscow", "urlName": "moscow"},
                    {"name": "Moscow", "urlName": "moscow-oblast"},
                ],
            },
        ],
    },
)
_CHART: Final[str] = "Rank,Artist,Title\n1,Artist,Title\n"
_CHARTS: Final[str] = "https://www.shazam.com/services/charts"
_LOCATIONS_ROUTE: Final[str] = f"{_CHARTS}/locations"
_GOOD_APPLE_ID: Final[int] = 1125281672
# The same recording as `1440650711`, under the id Shazam stores rather than the
#  one a caller asks for.
_CANONICALIZED_APPLE_ID: Final[int] = 1440650711
# Five Apple songs, three of them versions of one Shazam track.
_QUERY_WITH_SHARED_TRACKS: Final[str] = "daft punk one more time"
_TWO_SONGS: Final[str] = json.dumps({"results": [{"trackId": 697195462}, {"trackId": 697402071}]})


def _content_type_of(url: str) -> str:
    if url.startswith(service.CHART_URL.partition("{")[0]):
        return _CSV

    if url.startswith(service.ITUNES_SEARCH_URL):
        return service.ITUNES_SEARCH_CONTENT_TYPE

    return _JSON


def _answer_every_request(
    monkeypatch: pytest.MonkeyPatch,
    *,
    answers: dict[str, str],
) -> MockTransport:
    """Answer each request with the body for its endpoint's content type."""

    def answer(request: Request) -> Response:
        content_type = _content_type_of(request.url)

        return Response(
            status=HTTPStatus.OK,
            content_type=content_type,
            text=answers[content_type],
        )

    monkeypatch.setattr(service, "headers", lambda _language: _HEADERS)

    return MockTransport(answer)


def _sent(transport: MockTransport) -> list[dict[str, Any]]:
    return [
        {
            "method": request.method,
            "route": _UUID.sub("<uuid>", request.url.partition("?")[0]),
            "headers": request.headers,
        }
        for request in transport.requests
    ]


@pytest.fixture(scope="session")
def song_bytes() -> bytes:
    return _GLORIA.read_bytes()


@pytest.mark.vcr
@pytest.mark.asyncio
async def test_recognize_file(shazam: Shazam) -> None:
    out = await shazam.recognize(data=_GLORIA)

    assert out.track is not None
    assert out.track.key == 53982678


@pytest.mark.vcr
@pytest.mark.asyncio
async def test_recognize_bytes(
    song_bytes: bytes,
    shazam: Shazam,
) -> None:
    out = await shazam.recognize(data=song_bytes)

    assert out.track is not None
    assert out.track.key == 53982678


async def test_data_that_is_neither_a_path_nor_bytes_is_rejected(shazam: Shazam) -> None:
    with pytest.raises(TypeError, match="must be a path or bytes"):
        await shazam.recognize(42)  # type: ignore[arg-type]


@pytest.mark.parametrize(
    ("seconds", "match"),
    [
        pytest.param(10, "clients send a 12 s window", id="core-default"),
        pytest.param(14, "clients send a 12 s window", id="below-no-match"),
        pytest.param(15, "returns no matches", id="no-match-floor"),
    ],
)
async def test_a_window_other_than_twelve_warns_at_the_caller(
    shazam: Shazam,
    *,
    seconds: int,
    match: str,
) -> None:
    # A missing file fails in the fingerprinting, after the check and before any request.
    with pytest.warns(UserWarning, match=match) as record, pytest.raises(SignatureError):
        await shazam.recognize(
            "missing.ogg",
            options=SearchParams(segment_duration_seconds=seconds),
        )

    assert record[0].filename == __file__


async def test_a_twelve_second_window_does_not_warn(shazam: Shazam) -> None:
    with warnings.catch_warnings():
        warnings.simplefilter("error")

        with pytest.raises(SignatureError):
            await shazam.recognize(
                "missing.ogg",
                options=SearchParams(segment_duration_seconds=12),
            )


def _answer(
    *,
    timeskew: float,
    frequencyskew: float,
) -> ResponseTrack:
    return ResponseTrack.model_validate(
        {
            "matches": [
                {
                    "id": "53982678",
                    "offset": 0.0,
                    "timeskew": timeskew,
                    "frequencyskew": frequencyskew,
                },
            ],
            "track": {"key": "53982678", "title": "I Will Survive", "subtitle": "Gloria Gaynor"},
            "tagid": _TAG_ID,
        },
    )


def _answer_with(
    monkeypatch: pytest.MonkeyPatch,
    *,
    shazam: Shazam,
    answer: ResponseTrack,
) -> None:
    async def send(sig: Signature) -> ResponseTrack:
        del sig  # The answer is fixed; the signature is never sent.
        return answer

    monkeypatch.setattr(shazam, "recognize_signature", send)


@pytest.mark.parametrize(
    ("answer", "max_skew", "rejected"),
    [
        pytest.param(
            _answer(
                timeskew=-5e-4,
                frequencyskew=5e-4,
            ),
            1e-3,
            False,
            id="within",
        ),
        pytest.param(
            _answer(
                timeskew=1e-3,
                frequencyskew=0.0,
            ),
            1e-3,
            False,
            id="at-the-limit",
        ),
        pytest.param(
            _answer(
                timeskew=-2e-3,
                frequencyskew=0.0,
            ),
            1e-3,
            True,
            id="time-beyond",
        ),
        pytest.param(
            _answer(
                timeskew=0.0,
                frequencyskew=2e-3,
            ),
            1e-3,
            True,
            id="frequency-beyond",
        ),
        pytest.param(
            _answer(
                timeskew=2e-2,
                frequencyskew=0.0,
            ),
            None,
            False,
            id="off-by-default",
        ),
    ],
)
async def test_max_skew_rejects_a_skewed_first_match(
    monkeypatch: pytest.MonkeyPatch,
    shazam: Shazam,
    answer: ResponseTrack,
    max_skew: float | None,
    # pytest passes parametrize arguments by keyword, so no call site holds a bare `True`.
    rejected: bool,  # noqa: FBT001
) -> None:
    _answer_with(
        monkeypatch,
        shazam=shazam,
        answer=answer,
    )

    out = await shazam.recognize(_GLORIA, max_skew=max_skew)

    assert out == (_NO_MATCH if rejected else answer)


async def test_max_skew_keeps_a_no_match(
    monkeypatch: pytest.MonkeyPatch,
    shazam: Shazam,
) -> None:
    _answer_with(
        monkeypatch,
        shazam=shazam,
        answer=_NO_MATCH,
    )

    out = await shazam.recognize(_GLORIA, max_skew=1e-3)

    assert out == _NO_MATCH


@pytest.mark.parametrize(
    "max_skew",
    [
        pytest.param(0.0, id="zero"),
        pytest.param(-1e-3, id="negative"),
        pytest.param(float("nan"), id="nan"),
    ],
)
async def test_max_skew_must_be_positive(
    shazam: Shazam,
    max_skew: float,
) -> None:
    with pytest.raises(ValueError, match="must be above 0"):
        await shazam.recognize(_GLORIA, max_skew=max_skew)


@pytest.mark.parametrize(
    ("options", "segment"),
    [
        pytest.param({}, "iphone", id="default"),
        pytest.param({"recognition_device": Device.IPHONE}, "iphone", id="iphone"),
        pytest.param({"recognition_device": Device.ANDROID}, "android", id="android"),
        pytest.param({"recognition_device": Device.WEB}, "web", id="web"),
        pytest.param({"recognition_device": "android"}, "android", id="plain-string"),
    ],
)
async def test_the_device_changes_only_the_recognition_route(
    monkeypatch: pytest.MonkeyPatch,
    *,
    options: dict[str, Any],
    segment: str,
) -> None:
    transport = _answer_every_request(
        monkeypatch,
        answers={_JSON: json.dumps({"matches": [], "tagid": _TAG_ID})},
    )

    async with Shazam(transport=transport, **options) as shazam:
        await shazam.recognize(_GLORIA)

    assert _sent(transport) == [
        {
            "method": "POST",
            "route": f"{_ROUTE}/{segment}/-/tag/<uuid>/<uuid>",
            "headers": {**_HEADERS, "Content-Type": _JSON},
        },
    ]


async def test_the_device_leaves_the_track_lookup_on_iphone(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    transport = _answer_every_request(
        monkeypatch,
        answers={_JSON: _GLORIA_TRACK},
    )

    async with Shazam(
        transport=transport,
        recognition_device=Device.ANDROID,
    ) as shazam:
        await shazam.track_about(53982678)

    assert _sent(transport) == [
        {"method": "GET", "route": f"{_ROUTE}/iphone/-/track/53982678", "headers": _HEADERS},
    ]


def test_an_unknown_device_is_rejected() -> None:
    with pytest.raises(ValueError, match="not a valid Device"):
        Shazam(recognition_device="unsupported")  # type: ignore[arg-type]


class _Lookup(Protocol):
    async def __call__(self, shazam: Shazam) -> None:
        """Ask `shazam` for one answer."""


async def _track_about(shazam: Shazam) -> None:
    await shazam.track_about(track_id=1)


async def _youtube(shazam: Shazam) -> None:
    await shazam.get_youtube_data(link="https://video.example/youtube")


async def _recognize(shazam: Shazam) -> None:
    await shazam.recognize(_GLORIA)


@pytest.mark.parametrize(
    ("lookup", "payload"),
    [
        pytest.param(_track_about, _UNKNOWN_SECTION, id="track-about"),
        pytest.param(_youtube, {"caption": "c"}, id="youtube"),
        pytest.param(_recognize, {"tagid": "x", "track": _UNKNOWN_SECTION}, id="recognize"),
        pytest.param(_track_about, "<!doctype html>", id="not-json"),
    ],
)
async def test_an_answer_the_model_rejects_raises_bad_payload(
    monkeypatch: pytest.MonkeyPatch,
    *,
    lookup: _Lookup,
    payload: dict[str, Any] | str,
) -> None:
    body = payload if isinstance(payload, str) else json.dumps(payload)
    transport = _answer_every_request(monkeypatch, answers={_JSON: body})
    shazam = Shazam(transport=transport)

    with pytest.raises(BadPayload, match="Shazam answer is not a"):
        await lookup(shazam)


async def test_the_youtube_lookup_sends_the_shazam_headers(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    transport = _answer_every_request(monkeypatch, answers={_JSON: _VIDEO})
    shazam = Shazam(transport=transport)

    await shazam.get_youtube_data(link=_LINK)

    assert _sent(transport) == [
        {"method": "GET", "route": "https://video.example/youtube/video", "headers": _HEADERS},
    ]


@pytest.mark.vcr
@pytest.mark.asyncio
async def test_a_recognized_track_leads_to_its_youtube_video(shazam: Shazam) -> None:
    track = (await shazam.recognize(data=_GLORIA)).track
    assert track is not None
    assert track.youtube_link is not None

    video = await shazam.get_youtube_data(link=track.youtube_link)

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


# The whole list of requests, not the last one: a city chart once fetched the
#  locations twice, once for the country and once for the city.
@pytest.mark.parametrize(
    ("chart", "routes"),
    [
        pytest.param({}, [f"{_CHARTS}/csv/top-200/world/"], id="world"),
        pytest.param(
            {"genre": GenreMusic.POP},
            [f"{_CHARTS}/csv/genre/world/pop/"],
            id="world-genre",
        ),
        pytest.param(
            {"genre": "k-pop"},
            [f"{_CHARTS}/csv/genre/world/k-pop/"],
            id="world-genre-string",
        ),
        pytest.param(
            {"country_code": "RU"},
            [_LOCATIONS_ROUTE, f"{_CHARTS}/csv/top-200/russia/"],
            id="country",
        ),
        pytest.param(
            {"country_code": "RU", "genre": GenreMusic.ROCK},
            [_LOCATIONS_ROUTE, f"{_CHARTS}/csv/genre/russia/rock/"],
            id="country-genre",
        ),
        pytest.param(
            {"country_code": "RU", "city": "Moscow"},
            [_LOCATIONS_ROUTE, f"{_CHARTS}/csv/top-50/russia/moscow/"],
            id="city",
        ),
    ],
)
async def test_the_chart_path_is_built_from_the_location_slugs(
    monkeypatch: pytest.MonkeyPatch,
    *,
    chart: dict[str, Any],
    routes: list[str],
) -> None:
    transport = _answer_every_request(monkeypatch, answers={_JSON: _LOCATIONS, _CSV: _CHART})
    shazam = Shazam(transport=transport)

    await shazam.top_tracks(**chart)

    assert [request["route"] for request in _sent(transport)] == routes


@pytest.mark.parametrize(
    ("country_code", "city"),
    [
        pytest.param("XX", None, id="unknown-country"),
        pytest.param("RU", "Minsk", id="unknown-city"),
    ],
)
async def test_an_unknown_location_is_rejected(
    monkeypatch: pytest.MonkeyPatch,
    *,
    country_code: str,
    city: str | None,
) -> None:
    transport = _answer_every_request(monkeypatch, answers={_JSON: _LOCATIONS, _CSV: _CHART})
    shazam = Shazam(transport=transport)

    with pytest.raises(NotFound):
        await shazam.top_tracks(country_code, city=city)

    assert [request["route"] for request in _sent(transport)] == [_LOCATIONS_ROUTE]


@pytest.mark.parametrize(
    ("country_code", "genre", "match"),
    [
        pytest.param(None, None, "needs its `country_code`", id="city-without-country"),
        pytest.param("RU", GenreMusic.POP, "no genre chart for a city", id="city-with-genre"),
    ],
)
async def test_a_city_chart_nobody_publishes_is_refused_before_any_request(
    monkeypatch: pytest.MonkeyPatch,
    *,
    country_code: str | None,
    genre: GenreMusic | None,
    match: str,
) -> None:
    transport = _answer_every_request(monkeypatch, answers={})
    shazam = Shazam(transport=transport)

    with pytest.raises(ValueError, match=match):
        await shazam.top_tracks(
            country_code,
            city="Moscow",
            genre=genre,
        )

    assert _sent(transport) == []


async def test_an_unknown_genre_is_refused_before_any_request(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    transport = _answer_every_request(monkeypatch, answers={})
    shazam = Shazam(transport=transport)

    with pytest.raises(ValueError, match="not a valid GenreMusic"):
        await shazam.top_tracks("RU", genre="no-such-genre")

    assert _sent(transport) == []


@pytest.mark.vcr
@pytest.mark.asyncio
async def test_the_world_chart_carries_two_hundred_ranked_entries(
    caplog: pytest.LogCaptureFixture,
    shazam: Shazam,
) -> None:
    tracks = await shazam.top_tracks()

    assert len(tracks) == 200
    assert [track.rank for track in tracks[:3]] == [1, 2, 3]

    # The library skips an odd row, but a live re-record has to fail on one,
    #  or the `cassettes` workflow never uploads the answer that holds it.
    assert "parse_chart.skip" not in caplog.messages


@pytest.mark.vcr
@pytest.mark.asyncio
async def test_a_city_chart_resolves_its_country_and_city_slugs(
    caplog: pytest.LogCaptureFixture,
    shazam: Shazam,
) -> None:
    tracks = await shazam.top_tracks("RU", city="Moscow")

    assert [track.rank for track in tracks[:5]] == [1, 2, 3, 4, 5]
    assert "parse_chart.skip" not in caplog.messages


# Parametrized rather than sampled: a genre Shazam renames stops having a chart
#  and answers `404`, which is how `regional-mexicano` left the enum.
@pytest.mark.vcr
@pytest.mark.asyncio
@pytest.mark.parametrize(
    "genre",
    [pytest.param(genre, id=genre.value) for genre in GenreMusic],
)
async def test_a_world_genre_chart_answers_for_every_genre_the_enum_carries(
    caplog: pytest.LogCaptureFixture,
    genre: GenreMusic,
    shazam: Shazam,
) -> None:
    tracks = await shazam.top_tracks(genre=genre)

    assert [track.rank for track in tracks[:5]] == [1, 2, 3, 4, 5]
    assert "parse_chart.skip" not in caplog.messages


@pytest.mark.asyncio
async def test_no_ids_is_refused_before_anything_is_requested(shazam: Shazam) -> None:
    with pytest.raises(ValueError, match="No Apple ids"):
        await shazam.track_keys_from_apple_ids([])


# Also pins the path-segment order `service.APPLE_IDS_URL` documents: this
#  test fails as `NotFound` if the two are ever swapped.
@pytest.mark.vcr
@pytest.mark.asyncio
async def test_an_apple_id_resolves_to_a_shazam_track_key(shazam: Shazam) -> None:
    keys = await shazam.track_keys_from_apple_ids([_GOOD_APPLE_ID])

    assert list(keys) == [str(_GOOD_APPLE_ID)]
    assert keys[str(_GOOD_APPLE_ID)].isdigit()


@pytest.mark.vcr
@pytest.mark.asyncio
async def test_the_map_is_keyed_by_the_ids_shazam_stores(shazam: Shazam) -> None:
    keys = await shazam.track_keys_from_apple_ids([_GOOD_APPLE_ID, _CANONICALIZED_APPLE_ID])

    assert len(keys) == 2
    assert str(_CANONICALIZED_APPLE_ID) not in keys


# Each of these resolves on its own to `56670613`, keyed by itself; together they
#  answer one entry, keyed by `6781023657`, which is neither of them.
@pytest.mark.vcr
@pytest.mark.asyncio
async def test_ids_sharing_one_track_collapse_into_a_single_entry(shazam: Shazam) -> None:
    keys = await shazam.track_keys_from_apple_ids([6781027645, 6781024437])

    assert len(keys) == 1
    assert "6781027645" not in keys
    assert "6781024437" not in keys


@pytest.mark.vcr
@pytest.mark.asyncio
async def test_an_id_the_service_cannot_resolve_at_all_is_reported(shazam: Shazam) -> None:
    with pytest.raises(NotFound, match="Could not fetch ids"):
        await shazam.track_keys_from_apple_ids([0])


@pytest.mark.vcr
@pytest.mark.asyncio
async def test_songs_sharing_a_shazam_track_come_back_once(shazam: Shazam) -> None:
    tracks = await shazam.search_tracks_via_itunes(_QUERY_WITH_SHARED_TRACKS)
    track_keys = [track.key for track in tracks]

    assert 0 < len(track_keys) < 5
    assert len(set(track_keys)) == len(track_keys)


@pytest.mark.parametrize(
    "limit",
    [
        pytest.param(0, id="zero"),
        pytest.param(201, id="above-apple-maximum"),
    ],
)
@pytest.mark.asyncio
async def test_a_limit_apple_does_not_serve_is_rejected(
    shazam: Shazam,
    limit: int,
) -> None:
    # Apple answers `limit=0` with 20 songs, so without the check this returns tracks.
    with pytest.raises(ValueError, match="limit"):
        await shazam.search_tracks_via_itunes(_QUERY_WITH_SHARED_TRACKS, limit=limit)


class _FailFirstWaitSecond:
    """Fails the call for the first subject and parks the call for the second."""

    def __init__(self, first: int) -> None:
        self._first = first
        self._cancelled: bool = False

    @property
    def cancelled(self) -> bool:
        return self._cancelled

    async def __call__(self, subject: int) -> None:
        if subject == self._first:
            await asyncio.sleep(0)
            msg: str = "Could not fetch ids"
            raise NotFound(msg)

        try:
            await asyncio.Event().wait()
        except asyncio.CancelledError:
            self._cancelled = True
            raise


@pytest.mark.asyncio
async def test_a_failed_mapping_cancels_the_other_mappings(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    call = _FailFirstWaitSecond(first=697195462)

    async def track_keys(apple_ids: list[int]) -> dict[str, str]:
        await call(apple_ids[0])
        return {}

    transport = _answer_every_request(
        monkeypatch,
        answers={service.ITUNES_SEARCH_CONTENT_TYPE: _TWO_SONGS},
    )
    shazam = Shazam(transport=transport)
    monkeypatch.setattr(shazam, "track_keys_from_apple_ids", track_keys)

    with pytest.raises(NotFound):
        await shazam.search_tracks_via_itunes(_QUERY_WITH_SHARED_TRACKS, limit=2)

    assert call.cancelled


@pytest.mark.asyncio
async def test_a_failed_track_cancels_the_other_tracks(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    call = _FailFirstWaitSecond(first=1)
    track_key_by_apple_id: dict[int, str] = {697195462: "1", 697402071: "2"}

    async def track_keys(apple_ids: list[int]) -> dict[str, str]:
        return {str(apple_ids[0]): track_key_by_apple_id[apple_ids[0]]}

    async def track_about(track_id: int) -> TrackInfo:
        await call(track_id)
        return TrackInfo(
            key=track_id,
            title="",
            subtitle="",
        )

    transport = _answer_every_request(
        monkeypatch,
        answers={service.ITUNES_SEARCH_CONTENT_TYPE: _TWO_SONGS},
    )
    shazam = Shazam(transport=transport)
    monkeypatch.setattr(shazam, "track_keys_from_apple_ids", track_keys)
    monkeypatch.setattr(shazam, "track_about", track_about)

    with pytest.raises(NotFound):
        await shazam.search_tracks_via_itunes(_QUERY_WITH_SHARED_TRACKS, limit=2)

    assert call.cancelled


def _answering_once(response: Response) -> MockTransport:
    def answer(_request: Request) -> Response:
        return response

    return MockTransport(answer)


@pytest.mark.asyncio
async def test_a_chart_that_is_not_published_names_its_status() -> None:
    shazam = Shazam(
        transport=_answering_once(
            Response(
                status=HTTPStatus.NOT_FOUND,
                content_type="text/html",
                text="",
            ),
        ),
    )

    with pytest.raises(BadResponse, match="404") as raised:
        await shazam.top_tracks()

    assert (raised.value.url, raised.value.status) == (
        service.CHART_URL.format(path=service.chart_path()),
        HTTPStatus.NOT_FOUND,
    )


@pytest.mark.asyncio
async def test_a_path_answered_by_the_website_names_the_content_type() -> None:
    shazam = Shazam(
        transport=_answering_once(
            Response(
                status=HTTPStatus.OK,
                content_type="text/html",
                text="<html></html>",
            ),
        ),
    )

    with pytest.raises(BadResponse, match="text/html") as raised:
        await shazam.top_tracks()

    assert not isinstance(raised.value, RateLimited)


# Both answers are `text/html`, and only the throttled one is a rate limit:
#  the test above is the control that a guard firing on every HTML body fails.
@pytest.mark.asyncio
async def test_a_throttled_request_names_the_rate_limit() -> None:
    transport = _answering_once(
        Response(
            status=HTTPStatus.TOO_MANY_REQUESTS,
            content_type="text/html",
            text="<html></html>",
        ),
    )
    shazam = Shazam(
        transport=transport,
        middleware=(),
    )

    with pytest.raises(RateLimited, match="rate limited") as raised:
        await shazam.track_about(1)

    assert raised.value.status == HTTPStatus.TOO_MANY_REQUESTS
    assert len(transport.requests) == 1


# A transport may define `__len__`, a queue of canned answers for one, and an
#  empty one is falsy, which must not swap in the default network transport.
class _EmptyQueueTransport(MockTransport):
    def __len__(self) -> int:
        return 0


@pytest.mark.asyncio
async def test_a_falsy_transport_still_carries_the_requests() -> None:
    def answer(_request: Request) -> Response:
        return Response(
            status=HTTPStatus.OK,
            content_type=_JSON,
            text=_GLORIA_TRACK,
        )

    transport = _EmptyQueueTransport(answer)

    async with Shazam(transport=transport) as shazam:
        await shazam.track_about(53982678)

    assert len(transport.requests) == 1


# `MockTransport` has no closed state of its own, so only the client's guard
#  can refuse here.
@pytest.mark.asyncio
async def test_a_request_after_shazam_is_closed_is_refused() -> None:
    transport = _answering_once(
        Response(
            status=HTTPStatus.OK,
            content_type=_JSON,
            text=_GLORIA_TRACK,
        ),
    )
    shazam = Shazam(transport=transport)
    await shazam.close()

    with pytest.raises(RuntimeError, match="Shazam is closed"):
        await shazam.track_about(53982678)

    assert transport.requests == []
