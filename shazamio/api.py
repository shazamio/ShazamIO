import pathlib
import time
import uuid
from typing import Any

from aiohttp_retry import ExponentialRetry
from pydub import AudioSegment
from shazamio_core import Recognizer, SearchParams, Signature

from .charts import CHART_CONTENT_TYPE, parse_chart_csv
from .client import HTTPClient
from .converter import Converter
from .deprecated.decorator import deprecated
from .enums import GenreMusic
from .geo import GeoService
from .interfaces.client import HTTPClientInterface
from .misc import Device, Request, ShazamUrl
from .schemas.charts import ChartTrack
from .signature import DecodedMessage
from .typehints import CountryCode
from .utils import get_song


class Shazam(Request):
    """Is asynchronous framework for reverse engineered Shazam API written in Python 3.10+ with
    asyncio and aiohttp.
    """

    def __init__(
        self,
        language: str = "en-US",
        endpoint_country: str = "GB",
        http_client: HTTPClientInterface | None = None,
        segment_duration_seconds: int = 10,
    ) -> None:
        super().__init__(language=language)

        self.core_recognizer = Recognizer(
            segment_duration_seconds=segment_duration_seconds,
        )
        self.language = language
        self.endpoint_country = endpoint_country

        self.http_client = http_client or HTTPClient(
            retry_options=ExponentialRetry(
                attempts=20,
                max_timeout=60,
                statuses={500, 502, 503, 504, 429},
            ),
        )
        self.geo_service = GeoService(self.http_client, request=self)

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

    @deprecated("Use recognize method instead of recognize_song")
    async def recognize_song(
        self,
        data: str | pathlib.Path | bytes | bytearray | AudioSegment,
        proxy: str | None = None,
    ) -> dict[str, Any]:
        """Creating a song signature based on a file and searching for this signature in the shazam
        database.
            :param data: Path to song file or bytes
            :param proxy: Proxy server
            :return: Dictionary with information about the found song.
        """
        song = await get_song(data=data)
        audio = Converter.normalize_audio_data(song)
        signature_generator = Converter.create_signature_generator(audio)
        signature = signature_generator.get_next_signature()

        if signature is None:
            return {"matches": []}

        return await self.send_recognize_request(
            signature,
            proxy=proxy,
        )

    async def send_recognize_request(
        self,
        sig: DecodedMessage,
        proxy: str | None = None,
    ) -> dict[str, Any]:
        data = Converter.data_search(
            Request.TIME_ZONE,
            sig.encode_to_uri(),
            int(sig.number_samples / sig.sample_rate_hz * 1000),
            int(time.time() * 1000),
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

    async def recognize(
        self,
        data: str | pathlib.Path | bytes | bytearray,
        proxy: str | None = None,
        options: SearchParams | None = None,
    ) -> dict[str, Any]:
        """All logic and mathematics are transferred to RUST lang.

        Creating a song signature based on a file and searching for this signature in the shazam
        database.
            :param data: Path to song file or bytes
            :param proxy: Proxy server
            :param options: Search parameters
            :return: Dictionary with information about the found song
        """
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
