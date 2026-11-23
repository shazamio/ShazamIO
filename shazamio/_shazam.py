import asyncio
import pathlib
import warnings
from collections.abc import Coroutine, Iterable, Sequence
from http import HTTPStatus
from types import TracebackType
from typing import Any, Final, Self, TypeVar

from shazamio_core import Recognizer, SearchParams, Signature

from shazamio import _service as service
from shazamio._endpoint import Endpoint, Settings
from shazamio._enums import Device, GenreMusic
from shazamio._exceptions import BadResponse, NotFound, RateLimited
from shazamio._middleware import Middleware, chain
from shazamio._retry import Retry
from shazamio._transport import AiohttpTransport, Response, Transport
from shazamio.endpoints import (
    ItunesSearch,
    RecognizeSignature,
    TrackAbout,
    TrackKeysFromAppleIds,
    YoutubeVideo,
    _Chart,
    _ChartLocations,
)
from shazamio.models import ChartTrack, ResponseTrack, TrackInfo, YoutubeData

__all__ = [
    "WINDOW_SECONDS",
    "Shazam",
]


# The window SongRec sends, 12 s:
#  https://github.com/marin-m/SongRec/blob/b94ee61d51f40e8b3051da8f5c6a9e9c437b3633/src/core/fingerprinting/algorithm.rs#L77-L99
WINDOW_SECONDS: Final[int] = 12
# Shazam answers `matches: []` from 15 s up, for any track:
#  https://github.com/shazamio/ShazamIO/issues/150
_NO_MATCH_WINDOW_SECONDS: Final[int] = 15

# PEP 695 generics need Python 3.12, and the package supports 3.11.
_Result = TypeVar("_Result")
_Answer = TypeVar("_Answer")


def _read(
    response: Response,
    *,
    url: str,
    content_type: str,
) -> str:
    # A throttled request carries no answer, so without this it surfaces as a
    #  content-type error naming something the rate limiter did. `SongRec`
    #  reports the status by name too:
    #  https://github.com/marin-m/SongRec/blob/b94ee61d51f40e8b3051da8f5c6a9e9c437b3633/src/core/fingerprinting/communication.rs#L120
    if response.status == HTTPStatus.TOO_MANY_REQUESTS:
        msg = f"{url} rate limited the request"
        raise RateLimited(
            msg,
            url=url,
            status=response.status,
        )

    if response.status != HTTPStatus.OK:
        msg = f"{url} answered {response.status}"
        raise BadResponse(
            msg,
            url=url,
            status=response.status,
        )

    # A path the edge does not route to the API is answered by the website
    #  itself, `200 text/html`, so the status alone says nothing about the body.
    #  Without this the caller gets a parse error naming the parser.
    if response.content_type != content_type:
        msg = f"{url} answered {response.content_type}, expected {content_type}"
        raise BadResponse(
            msg,
            url=url,
            status=response.status,
        )

    return response.text


def _warn_on_window(seconds: int) -> None:
    if seconds >= _NO_MATCH_WINDOW_SECONDS:
        msg = (
            f"segment_duration_seconds={seconds}: Shazam returns no matches for a window of "
            f"{_NO_MATCH_WINDOW_SECONDS} s or more, use {WINDOW_SECONDS}"
        )
    elif seconds != WINDOW_SECONDS:
        msg = (
            f"segment_duration_seconds={seconds}: Shazam clients send a {WINDOW_SECONDS} s window, "
            "keep it unless you measured another"
        )
    else:
        return

    # Points at the caller of `recognize()`, not at this helper.
    warnings.warn(msg, UserWarning, stacklevel=3)


def _reject_skewed(
    answer: ResponseTrack,
    *,
    max_skew: float,
) -> ResponseTrack:
    if not answer.matches:
        return answer

    first = answer.matches[0]
    skew: float = max(abs(first.time_skew), abs(first.frequency_skew))
    if skew <= max_skew:
        return answer

    # `track` describes the first match only, so it goes with it.
    return answer.model_copy(update={"matches": [], "track": None})


# `asyncio.gather` leaves the other calls running when one raises, so a failed
#  search kept sending requests after it had raised:
#  https://docs.python.org/3.11/library/asyncio-task.html#asyncio.gather
#  `asyncio.TaskGroup` cancels them too, but wraps the error in an `ExceptionGroup`,
#  so a caller's `except` for it would stop matching.
#  https://docs.python.org/3.11/library/asyncio-task.html#task-groups
async def _gather_or_cancel(calls: Iterable[Coroutine[Any, Any, _Result]]) -> list[_Result]:
    tasks = [asyncio.ensure_future(call) for call in calls]

    try:
        return await asyncio.gather(*tasks)
    finally:
        for task in tasks:
            task.cancel()
        await asyncio.gather(*tasks, return_exceptions=True)


class Shazam:
    """Async client for the Shazam API.

    `transport` sends the requests, `AiohttpTransport()` unless given. Every request
    passes through `middleware` on its way, the first one outermost; `(Retry(),)`
    unless given, and `()` sends each request once. `close()` closes the transport.
    """

    __module__ = "shazamio"

    def __init__(
        self,
        *,
        language: str = "en-US",
        country: str = "GB",
        transport: Transport | None = None,
        middleware: Sequence[Middleware] | None = None,
        recognition_device: Device = Device.IPHONE,
    ) -> None:
        self._settings = Settings(
            language=language,
            country=country,
            device=Device(recognition_device),
        )
        self._recognizer = Recognizer(segment_duration_seconds=WINDOW_SECONDS)
        self._transport: Transport = transport if transport is not None else AiohttpTransport()
        self._owns_transport: bool = transport is None
        self._call_next = chain(
            (Retry(),) if middleware is None else middleware,
            transport=self._transport,
        )
        self._closed: bool = False

    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        await self.close()

    async def close(self) -> None:
        """Close the transport `Shazam` built. A call after this raises `RuntimeError`."""
        self._closed = True

        if self._owns_transport:
            await self._transport.close()

    async def __call__(self, endpoint: Endpoint[_Answer]) -> _Answer:
        """Send the request of `endpoint` and return its answer.

        :raises TransportError: no answer arrived
        :raises RateLimited: the service answered `429`
        :raises BadResponse: another status than `200`, or another content type
        :raises BadPayload: the answer does not fit `endpoint`
        """
        if self._closed:
            msg: str = "Shazam is closed"
            raise RuntimeError(msg)

        request = endpoint.request(self._settings)
        response = await self._call_next(request)
        payload = _read(
            response,
            url=request.url,
            content_type=endpoint.content_type,
        )

        return endpoint.parse(payload)

    async def top_tracks(
        self,
        country_code: str | None = None,
        *,
        city: str | None = None,
        genre: GenreMusic | str | None = None,
    ) -> list[ChartTrack]:
        """The most shazamed tracks worldwide, in a country, a city or a genre.

        Worldwide and country charts carry 200 entries, city charts 50, genre charts
        50 to 200. Shazam offers only a handful of genres per country, and asking for
        one it does not offer answers `404`.

        :param country_code: ISO 3166-1 alpha-2 code, `None` for worldwide. Example: RU
        :param city: City name as `services/charts/locations` spells it. Example: Moscow
        :param genre: Genre, as a `GenreMusic` member or its value. Example: rock
        :return: chart entries, highest ranked first
        :raises ValueError: a city without a country, a city with a genre, or an unknown genre
        :raises NotFound: the country or the city has no chart
        """
        if city is not None and country_code is None:
            msg: str = "A city chart needs its `country_code`"
            raise ValueError(msg)

        if city is not None and genre is not None:
            msg: str = "Shazam publishes no genre chart for a city"
            raise ValueError(msg)

        genre_slug = None if genre is None else GenreMusic(genre).value

        if country_code is None:
            path = service.chart_path(genre=genre_slug)
        else:
            path = await self._country_path(
                country_code,
                city=city,
                genre_slug=genre_slug,
            )

        return await self(_Chart(path=path))

    async def _country_path(
        self,
        country_code: str,
        *,
        city: str | None,
        genre_slug: str | None,
    ) -> str:
        locations = await self(_ChartLocations())

        country = next((entry for entry in locations.countries if entry.code == country_code), None)
        if country is None:
            msg = f"Country not found, check the country code: {country_code}"
            raise NotFound(msg)

        if genre_slug is not None:
            return service.chart_path(
                country=country.url_name,
                genre=genre_slug,
            )

        if city is None:
            return service.chart_path(country=country.url_name)

        city_entry = next((entry for entry in country.cities if entry.name == city), None)
        if city_entry is None:
            msg = f"City not found, check the city name: {city}"
            raise NotFound(msg)

        return service.chart_path(
            country=country.url_name,
            city=city_entry.url_name,
        )

    async def track_about(self, track_id: int) -> TrackInfo:
        """Get a track by its Shazam key, such as `549952578`.

        :raises BadPayload: the answer does not fit the model
        """
        return await self(TrackAbout(track_id=track_id))

    async def track_keys_from_apple_ids(self, apple_ids: Sequence[int | str]) -> dict[str, str]:
        """Map Apple Music track ids to Shazam track keys, in one request.

        A call with several ids keys every entry by the Apple id Shazam stores, which
        can be one that was never sent: `[6781027645, 6781024437]` answers
        `{"6781023657": "56670613"}`. A call with a single id keys it by that id.
        Either way an id Shazam has no track for is absent, so the map can be shorter
        than the sequence asked for, and `{}` when nothing resolved.

        :param apple_ids: Apple Music track ids. Example: (1125281672, 1440650711)
        :return: Apple id to Shazam track key, as the service serves it
        :raises ValueError: no ids were given
        :raises NotFound: the service refused the whole request: a malformed id,
            or a storefront it does not serve
        """
        return await self(TrackKeysFromAppleIds(apple_ids=apple_ids))

    async def search_tracks_via_itunes(
        self,
        query: str,
        *,
        limit: int = 5,
    ) -> list[TrackInfo]:
        """Search Apple's iTunes index, then fetch the Shazam track of every song found.

        Shazam no longer has a text search, so relevance, order and coverage are
        Apple's. A song Shazam has no track for is left out, and songs sharing one
        Shazam track appear once, so the list can be shorter than `limit`. A call
        costs one search, one id mapping per song and one `track_about` per track:
        at most `2 * limit + 1` requests. Apple caps that search at about 20 calls a
        minute: https://performance-partners.apple.com/search-api

        :param query: Free text, as typed into a search box. Example: daft punk one more time
        :param limit: How many Apple songs to resolve, from 1 to 200
        :return: the tracks, in Apple's order
        :raises ValueError: `limit` is outside 1 to 200
        :raises BadPayload: a track answer does not fit `TrackInfo`
        """
        apple_ids = await self(
            ItunesSearch(
                query=query,
                limit=limit,
            ),
        )

        # One id per call: a batch keys its entries by the id Shazam stores, which
        #  can be one never sent, so its tracks could not be put in Apple's order.
        mappings = await _gather_or_cancel(
            self.track_keys_from_apple_ids([apple_id]) for apple_id in apple_ids
        )
        track_keys = dict.fromkeys(
            mapping[str(apple_id)]
            for apple_id, mapping in zip(apple_ids, mappings, strict=True)
            if str(apple_id) in mapping
        )

        return await _gather_or_cancel(self.track_about(int(track_key)) for track_key in track_keys)

    async def get_youtube_data(self, link: str) -> YoutubeData:
        """Get the YouTube video Shazam shows for a track, from its `youtube_link`.

        :raises BadPayload: the answer does not fit the model
        """
        return await self(YoutubeVideo(link=link))

    async def recognize(
        self,
        data: str | pathlib.Path | bytes | bytearray,
        *,
        options: SearchParams | None = None,
        max_skew: float | None = None,
    ) -> ResponseTrack:
        """Search the Shazam database for the signature of a song file or its bytes.

        :param data: Path to song file or bytes
        :param options: Search parameters
        :param max_skew: Off by default. Answer "no match" when the first match is skewed in
            time or in frequency by more than this fraction. Wrong answers tend to carry a
            larger skew than right ones: on 234 songs, `1e-3` rejected 23 of 28 wrong answers
            and 15 of 611 right ones. A right answer for audio played faster, slower or
            pitch-shifted carries that shift as its skew (about `0.02` for 2 %), so any useful
            limit rejects such audio too.
        :return: the answer, whose `track` is `None` when nothing matched
        :raises BadPayload: the answer does not fit the model
        :raises SignatureError: the audio cannot be read, a missing file included
        """
        # `not > 0` rather than `<= 0`: `nan <= 0` is `False`, so `NaN` would pass and then
        #  reject every answer, since no skew compares `<=` to it.
        if max_skew is not None and not max_skew > 0:
            msg = f"max_skew={max_skew}: must be above 0, or None to keep every answer"
            raise ValueError(msg)

        if options is not None:
            _warn_on_window(options.segment_duration_seconds)

        if isinstance(data, (str, pathlib.Path)):
            signature = await self._recognizer.recognize_path(
                value=data,
                options=options,
            )
        elif isinstance(data, (bytes, bytearray)):
            signature = await self._recognizer.recognize_bytes(
                value=data,
                options=options,
            )
        else:
            msg = f"`data` must be a path or bytes, got {type(data).__name__}"
            raise TypeError(msg)

        answer = await self.recognize_signature(signature)

        if max_skew is None:
            return answer

        return _reject_skewed(answer, max_skew=max_skew)

    async def recognize_signature(self, signature: Signature) -> ResponseTrack:
        """Search the Shazam database for a signature `shazamio_core` computed."""
        return await self(RecognizeSignature(signature=signature))
