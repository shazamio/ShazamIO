import asyncio
import pathlib
import uuid
import warnings
from collections.abc import Coroutine, Iterable, Sequence
from types import TracebackType
from typing import Any, Final, TypeVar

from aiohttp_retry import ExponentialRetry
from shazamio_core import Recognizer, SearchParams, Signature

from .apple import APPLE_TO_SHAZAM_CONTENT_TYPE, parse_apple_to_shazam_keys
from .charts import CHART_CONTENT_TYPE, parse_chart_csv
from .client import HTTPClient
from .converter import Converter
from .enums import GenreMusic
from .exceptions import BadAppleIds
from .geo import GeoService
from .interfaces.client import HTTPClientInterface
from .itunes import ITUNES_SEARCH_CONTENT_TYPE, ITUNES_SEARCH_MAX_LIMIT, parse_itunes_track_ids
from .misc import Device, Request, ShazamUrl
from .schemas.charts import ChartTrack
from .typehints import CountryCode

# The window SongRec sends, 12 s:
#  https://github.com/marin-m/SongRec/blob/b94ee61d51f40e8b3051da8f5c6a9e9c437b3633/src/core/fingerprinting/algorithm.rs#L77-L99
WINDOW_SECONDS: Final[int] = 12
# Shazam answers `matches: []` from 15 s up, for any track:
#  https://github.com/shazamio/ShazamIO/issues/150
_NO_MATCH_WINDOW_SECONDS: Final[int] = 15

_Result = TypeVar("_Result")


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

    # Points at the caller of `Shazam()` or `recognize()`, not at this helper.
    warnings.warn(msg, UserWarning, stacklevel=3)


# `asyncio.gather` leaves the other calls running when one raises, so a failed
#  search kept sending requests after it had raised:
#  https://docs.python.org/3.10/library/asyncio-task.html#asyncio.gather
#  `asyncio.TaskGroup` cancels them, but it needs Python 3.11.
async def _gather_or_cancel(calls: Iterable[Coroutine[Any, Any, _Result]]) -> list[_Result]:
    tasks = [asyncio.ensure_future(call) for call in calls]
    try:
        return await asyncio.gather(*tasks)
    finally:
        for task in tasks:
            task.cancel()
        await asyncio.gather(*tasks, return_exceptions=True)


class Shazam(Request):
    """Is asynchronous framework for reverse engineered Shazam API written in Python 3.10+ with
    asyncio and aiohttp.
    """

    def __init__(
        self,
        language: str = "en-US",
        endpoint_country: str = "GB",
        http_client: HTTPClientInterface | None = None,
        segment_duration_seconds: int = WINDOW_SECONDS,
    ) -> None:
        super().__init__(language=language)

        _warn_on_window(segment_duration_seconds)

        self.core_recognizer = Recognizer(
            segment_duration_seconds=segment_duration_seconds,
        )
        self.language = language
        self.endpoint_country = endpoint_country

        # Only a client we built is ours to close: an injected one keeps its own
        #  lifetime, the way `aiohttp` leaves a connector it did not create alone.
        self._owned_http_client: HTTPClient | None = None

        if http_client is None:
            http_client = HTTPClient(
                retry_options=ExponentialRetry(
                    attempts=20,
                    max_timeout=60,
                    statuses={500, 502, 503, 504, 429},
                ),
            )
            self._owned_http_client = http_client

        self.http_client = http_client
        self.geo_service = GeoService(self.http_client, request=self)

    # `typing.Self` arrived in 3.11 and the floor is 3.10, so the class names
    #  itself here.
    async def __aenter__(self) -> "Shazam":  # noqa: PYI034
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        await self.close()

    async def close(self) -> None:
        """Close the pooled connections. A call after this raises `RuntimeError`."""
        if self._owned_http_client is not None:
            await self._owned_http_client.close()

    async def top_world_tracks(
        self,
        *,
        limit: int | None = None,
        offset: int = 0,
        proxy: str | None = None,
    ) -> list[ChartTrack]:
        """The most shazamed tracks worldwide, 200 of them.

        :param limit: How many entries to return. The default returns the whole chart.
        :param offset: How many entries to skip.
        :param proxy: Proxy server
        :return: chart entries, highest ranked first
        """
        return await self._chart(
            ShazamUrl.TOP_WORLD_TRACKS,
            limit=limit,
            offset=offset,
            proxy=proxy,
        )

    async def top_country_tracks(
        self,
        country_code: str,
        *,
        limit: int | None = None,
        offset: int = 0,
        proxy: str | None = None,
    ) -> list[ChartTrack]:
        """The most shazamed tracks in a country, 200 of them.

        :param country_code: ISO 3166-3 alpha-2 code. Example: RU, NL, UA
        :param limit: How many entries to return. The default returns the whole chart.
        :param offset: How many entries to skip.
        :param proxy: Proxy server
        :return: chart entries, highest ranked first
        """
        country = await self.geo_service.country_url_name(
            CountryCode(country_code),
            proxy=proxy,
        )

        return await self._chart(
            ShazamUrl.TOP_COUNTRY_TRACKS.format(country=country),
            limit=limit,
            offset=offset,
            proxy=proxy,
        )

    async def top_city_tracks(
        self,
        country_code: str,
        *,
        city_name: str,
        limit: int | None = None,
        offset: int = 0,
        proxy: str | None = None,
    ) -> list[ChartTrack]:
        """The most shazamed tracks in a city, 50 of them.

        :param country_code: ISO 3166-3 alpha-2 code. Example: RU, NL, UA
        :param city_name: City name as `services/charts/locations` spells it. Example: Moscow
        :param limit: How many entries to return. The default returns the whole chart.
        :param offset: How many entries to skip.
        :param proxy: Proxy server
        :return: chart entries, highest ranked first
        """
        country = CountryCode(country_code)
        city = await self.geo_service.city_url_name(
            country,
            city=city_name,
            proxy=proxy,
        )

        return await self._chart(
            ShazamUrl.TOP_CITY_TRACKS.format(
                country=await self.geo_service.country_url_name(country, proxy=proxy),
                city=city,
            ),
            limit=limit,
            offset=offset,
            proxy=proxy,
        )

    async def top_world_genre_tracks(
        self,
        genre: GenreMusic | str,
        *,
        limit: int | None = None,
        offset: int = 0,
        proxy: str | None = None,
    ) -> list[ChartTrack]:
        """The most shazamed tracks worldwide in one genre, 50 to 200 of them.

        :param genre: Genre, as a `GenreMusic` member or its value. Example: rock
        :param limit: How many entries to return. The default returns the whole chart.
        :param offset: How many entries to skip.
        :param proxy: Proxy server
        :return: chart entries, highest ranked first
        """
        return await self._chart(
            ShazamUrl.TOP_WORLD_GENRE_TRACKS.format(genre=GenreMusic(genre).value),
            limit=limit,
            offset=offset,
            proxy=proxy,
        )

    async def top_country_genre_tracks(
        self,
        country_code: str,
        *,
        genre: GenreMusic | str,
        limit: int | None = None,
        offset: int = 0,
        proxy: str | None = None,
    ) -> list[ChartTrack]:
        """The most shazamed tracks in a country in one genre, 100 of them.

        Shazam offers only a handful of genres per country, and asking for one it
        does not offer answers `404`.

        :param country_code: ISO 3166-3 alpha-2 code. Example: ES, RU, NL
        :param genre: Genre, as a `GenreMusic` member or its value. Example: hip-hop-rap
        :param limit: How many entries to return. The default returns the whole chart.
        :param offset: How many entries to skip.
        :param proxy: Proxy server
        :return: chart entries, highest ranked first
        """
        country = await self.geo_service.country_url_name(
            CountryCode(country_code),
            proxy=proxy,
        )

        return await self._chart(
            ShazamUrl.TOP_COUNTRY_GENRE_TRACKS.format(
                country=country,
                genre=GenreMusic(genre).value,
            ),
            limit=limit,
            offset=offset,
            proxy=proxy,
        )

    async def _chart(
        self,
        url: str,
        *,
        limit: int | None,
        offset: int,
        proxy: str | None,
    ) -> list[ChartTrack]:
        payload = await self.http_client.request_text(
            url,
            content_type=CHART_CONTENT_TYPE,
            headers=self.headers(),
            proxy=proxy,
        )
        tracks = parse_chart_csv(payload)

        return tracks[offset : None if limit is None else offset + limit]

    async def track_about(
        self,
        track_id: int,
        proxy: str | None = None,
    ) -> dict[str, Any]:
        """Get track information.

        :param track_id: Track number. Example: (549952578)
        https://www.shazam.com/track/549952578/
        :param proxy: Proxy server
        :return: dict about track
        """
        return await self.http_client.request(
            "GET",
            ShazamUrl.ABOUT_TRACK.format(
                language=self.language,
                endpoint_country=self.endpoint_country,
                track_id=track_id,
            ),
            headers=self.headers(),
            proxy=proxy,
        )

    async def related_tracks(
        self,
        track_id: int,
        limit: int = 20,
        offset: int = 0,
        proxy: str | None = None,
    ) -> dict[str, Any]:
        """Similar songs based song id
        https://www.shazam.com/track/546891609/2-phu%CC%81t-ho%CC%9Bn-kaiz-remix
            :param track_id: Track number. Example: (549952578)
            https://www.shazam.com/track/549952578/
            :param limit: Determines how many songs the maximum can be in the request.
                Example: If 5 is specified, the query will return no more than 5 songs
            :param offset: A parameter that determines with which song to display the request.
                The default is 0. If you want to skip the first few songs, set this parameter to
                your own.
            :param proxy: Proxy server
            :return: dict tracks.
        """
        return await self.http_client.request(
            "GET",
            ShazamUrl.RELATED_SONGS.format(
                language=self.language,
                endpoint_country=self.endpoint_country,
                limit=limit,
                offset=offset,
                track_id=track_id,
            ),
            headers=self.headers(),
            proxy=proxy,
        )

    async def track_keys_from_apple_ids(
        self,
        apple_ids: Sequence[int | str],
        *,
        proxy: str | None = None,
    ) -> dict[str, str]:
        """Map Apple Music track ids to Shazam track keys, in one request.

        A call with several ids keys every entry by the Apple id Shazam stores, which
        can be one that was never sent: `[6781027645, 6781024437]` answers
        `{"6781023657": "56670613"}`. A call with a single id keys it by that id.
        Either way an id Shazam has no track for is absent, so the map can be shorter
        than the sequence asked for, and `{}` when nothing resolved.

        :param apple_ids: Apple Music track ids. Example: (1125281672, 1440650711)
        :param proxy: Proxy server
        :return: Apple id to Shazam track key, as the service serves it
        :raises BadAppleIds: no ids were given, or the service refused the whole
            request: a malformed id, or a storefront it does not serve
        """
        # An empty sequence asks for `.../{language}/`, which answers
        #  `404 text/html Not supported` and reads as a dead endpoint.
        if not apple_ids:
            msg: str = "No Apple ids given"
            raise BadAppleIds(msg)

        payload = await self.http_client.request_text(
            ShazamUrl.APPLE_IDS_TO_TRACK_KEYS.format(
                country=self.endpoint_country,
                language=self.language,
                apple_ids=",".join(str(apple_id) for apple_id in apple_ids),
            ),
            content_type=APPLE_TO_SHAZAM_CONTENT_TYPE,
            headers=self.headers(),
            proxy=proxy,
        )

        return parse_apple_to_shazam_keys(payload)

    async def search_tracks_via_itunes(
        self,
        query: str,
        *,
        limit: int = 5,
        proxy: str | None = None,
    ) -> list[dict[str, Any]]:
        """Search Apple's iTunes index, then fetch the Shazam track of every song found.

        Shazam no longer has a text search, so relevance, order and coverage are
        Apple's. A song Shazam has no track for is left out, and songs sharing one
        Shazam track appear once, so the list can be shorter than `limit`. A call
        costs one search, one id mapping per song and one `track_about` per track:
        at most `2 * limit + 1` requests. Apple caps that search at about 20 calls a
        minute: https://performance-partners.apple.com/search-api

        :param query: Free text, as typed into a search box. Example: ("daft punk one more time")
        :param limit: How many Apple songs to resolve, from 1 to 200
        :param proxy: Proxy server
        :return: `track_about` answers, in Apple's order
        :raises ValueError: `limit` is outside 1 to 200
        """
        if not 1 <= limit <= ITUNES_SEARCH_MAX_LIMIT:
            msg = f"`limit` must be from 1 to {ITUNES_SEARCH_MAX_LIMIT}, got {limit}"
            raise ValueError(msg)

        payload = await self.http_client.request_text(
            ShazamUrl.ITUNES_SEARCH,
            content_type=ITUNES_SEARCH_CONTENT_TYPE,
            params={
                "term": query,
                "entity": "song",
                "limit": limit,
                "country": self.endpoint_country,
            },
            proxy=proxy,
        )
        apple_ids = parse_itunes_track_ids(payload)

        # One id per call: a batch keys its entries by the id Shazam stores, which
        #  can be one never sent, so its tracks could not be put in Apple's order.
        mappings = await _gather_or_cancel(
            self.track_keys_from_apple_ids([apple_id], proxy=proxy) for apple_id in apple_ids
        )
        track_keys = dict.fromkeys(
            mapping[str(apple_id)]
            for apple_id, mapping in zip(apple_ids, mappings, strict=True)
            if str(apple_id) in mapping
        )

        return await _gather_or_cancel(
            self.track_about(int(track_key), proxy=proxy) for track_key in track_keys
        )

    async def recognize(
        self,
        data: str | pathlib.Path | bytes | bytearray,
        proxy: str | None = None,
        options: SearchParams | None = None,
    ) -> dict[str, Any]:
        """Search the Shazam database for the signature of a song file or its bytes.

        :param data: Path to song file or bytes
        :param proxy: Proxy server
        :param options: Search parameters
        :return: Dictionary with information about the found song
        """
        if options is not None:
            _warn_on_window(options.segment_duration_seconds)

        if isinstance(data, (str, pathlib.Path)):
            signature = await self.core_recognizer.recognize_path(value=data, options=options)
        elif isinstance(data, (bytes, bytearray)):
            signature = await self.core_recognizer.recognize_bytes(value=data, options=options)
        else:
            # Callers have caught `ValueError` here since 0.x; switching to the
            #  `TypeError` the rule prefers is a breaking change, not a lint fix.
            msg: str = "Invalid data type"
            raise ValueError(msg)  # noqa: TRY004

        return await self.send_recognize_request_v2(sig=signature, proxy=proxy)

    async def send_recognize_request_v2(
        self,
        sig: Signature,
        proxy: str | None = None,
    ) -> dict[str, Any]:
        data = Converter.data_search(
            sig.timezone,
            sig.signature.uri,
            sig.signature.samples,
            sig.timestamp,
        )
        return await self.http_client.request(
            "POST",
            ShazamUrl.SEARCH_FROM_FILE.format(
                language=self.language,
                device=Device.IPHONE.value,
                endpoint_country=self.endpoint_country,
                uuid_1=str(uuid.uuid4()).upper(),
                uuid_2=str(uuid.uuid4()).upper(),
            ),
            headers=self.headers(),
            proxy=proxy,
            json=data,
        )
