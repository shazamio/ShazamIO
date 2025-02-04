import pathlib
import time
import uuid
from typing import Dict, Any, Union, List
from typing import Optional

from aiohttp_retry import ExponentialRetry
from pydub import AudioSegment
from shazamio_core import Recognizer, Signature, SearchParams

from .client import HTTPClient
from .converter import Converter, GeoService
from .deprecated.decorator import deprecated
from .enums import GenreMusic
from .interfaces.client import HTTPClientInterface
from .misc import Request, Device
from .misc import ShazamUrl
from .schemas.artists import ArtistQuery
from .signature import DecodedMessage
from .typehints import CountryCode
from .utils import ArtistQueryGenerator
from .utils import get_song


class Shazam(Request):
    """
    Is asynchronous framework for reverse engineered Shazam API written in Python 3.10+ with
    asyncio and aiohttp.
    """

    def __init__(
        self,
        language: str = "en-US",
        endpoint_country: str = "GB",
        http_client: Optional[HTTPClientInterface] = None,
        segment_duration_seconds: int = 10,
    ):
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
        self.geo_service = GeoService(self.http_client)

    async def top_world_tracks(
        self,
        limit: int = 200,
        offset: int = 0,
        proxy: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Search top world tracks

            :param limit: Determines how many songs the maximum can be in the request.
                Example: If 5 is specified, the query will return no more than 5 songs.
            :param offset: A parameter that determines with which song to display the request.
                The default is 0. If you want to skip the first few songs, set this parameter to
                your own.
            :param proxy: Proxy server
            :return: dict tracks
        """

        top_playlist_id = await self.geo_service.get_top()
        return await self.http_client.request(
            "GET",
            ShazamUrl.TOP_TRACKS_PLAYLIST.format(
                playlist_id=top_playlist_id,
                language=self.language,
                endpoint_country=self.endpoint_country,
                limit=limit,
                offset=offset,
            ),
            headers=self.headers(),
            proxy=proxy,
        )

    async def artist_about(
        self,
        artist_id: int,
        query: Optional[ArtistQuery] = None,
        proxy: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Retrieving information from an artist profile

            :param artist_id: Artist number. Example (203347991)
            :param query: Foo
            https://www.shazam.com/artist/203347991/
            :param proxy: Proxy server
            :return: dict about artist
        """

        if query:
            pg = ArtistQueryGenerator(source=query)
            params_dict = pg.params()
        else:
            params_dict = {}

        return await self.http_client.request(
            "GET",
            ShazamUrl.SEARCH_ARTIST_V2.format(
                endpoint_country=self.endpoint_country,
                artist_id=artist_id,
            ),
            params=params_dict,
            headers=self.headers(),
            proxy=proxy,
        )

    async def track_about(
        self,
        track_id: int,
        proxy: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Get track information

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

    async def top_country_tracks(
        self,
        country_code: str,
        limit: int = 200,
        offset: int = 0,
        proxy: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Get the best tracks by country code
        https://www.shazam.com/charts/discovery/netherlands

            :param country_code: ISO 3166-3 alpha-2 code. Example: RU,NL,UA
            :param limit: Determines how many songs the maximum can be in the request.
                Example: If 5 is specified, the query will return no more than 5 songs.
            :param offset: A parameter that determines with which song to display the request.
                The default is 0. If you want to skip the first few songs, set this parameter to
                your own.
            :param proxy: Proxy server
            :return: dict songs
        """
        country_playlist_id = await self.geo_service.get_country_playlist(
            country=CountryCode(country_code),
        )

        return await self.http_client.request(
            "GET",
            ShazamUrl.TOP_TRACKS_PLAYLIST.format(
                playlist_id=country_playlist_id,
                language=self.language,
                endpoint_country=self.endpoint_country,
                country_code=country_code,
                limit=limit,
                offset=offset,
            ),
            headers=self.headers(),
            proxy=proxy,
        )

    async def top_city_tracks(
        self,
        country_code: str,
        city_name: str,
        limit: int = 200,
        offset: int = 0,
        proxy: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Retrieving information from an artist profile
        https://www.shazam.com/charts/top-50/russia/moscow

            :param country_code: ISO 3166-3 alpha-2 code. Example: RU,NL,UA
            :param city_name: City name from https://github.com/dotX12/dotX12/blob/main/city.json
                Example: Budapest, Moscow
            :param limit: Determines how many songs the maximum can be in the request.
                Example: If 5 is specified, the query will return no more than 5 songs.
            :param offset: A parameter that determines with which song to display the request.
                The default is 0. If you want to skip the first few songs, set this parameter to
                your own.
            :param proxy: Proxy server

            :return: dict songs
        """
        city_playlist_id = await self.geo_service.get_city_playlist(
            country=CountryCode(country_code),
            city=city_name,
        )

        return await self.http_client.request(
            "GET",
            ShazamUrl.TOP_TRACKS_PLAYLIST.format(
                playlist_id=city_playlist_id,
                language=self.language,
                endpoint_country=self.endpoint_country,
                country_code=country_code,
                limit=limit,
                offset=offset,
            ),
            headers=self.headers(),
            proxy=proxy,
        )

    async def top_world_genre_tracks(
        self,
        genre: Union[GenreMusic, str],
        limit: int = 100,
        offset: int = 0,
        proxy: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Get world tracks by certain genre
        https://www.shazam.com/charts/genre/world/rock

            :param genre: Genre urlName from https://www.shazam.com/services/charts/locations
            :param limit: Determines how many songs the maximum can be in the request.
                    Example: If 5 is specified, the query will return no more than 5 songs.
            :param offset: A parameter that determines with which song to display the request.
                    The default is 0. If you want to skip the first few songs, set this parameter
                    to your own.
            :param proxy: Proxy server
            :return: dict songs
        """

        if isinstance(genre, str):
            genre = GenreMusic(genre)

        genre_playlist_id = await self.geo_service.get_genre(genre=genre)
        return await self.http_client.request(
            "GET",
            ShazamUrl.TOP_TRACKS_PLAYLIST.format(
                playlist_id=genre_playlist_id,
                language=self.language,
                endpoint_country=self.endpoint_country,
                limit=limit,
                offset=offset,
            ),
            headers=self.headers(),
            proxy=proxy,
        )

    async def top_country_genre_tracks(
        self,
        country_code: str,
        genre: Union[GenreMusic, str],
        limit: int = 200,
        offset: int = 0,
        proxy: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        The best tracks by a genre in the country
        https://www.shazam.com/charts/genre/spain/hip-hop-rap
            :param country_code: ISO 3166-3 alpha-2 code. Example: RU,NL,UA
            :param genre: Genre name or ID:
                POP = 1, HIP_HOP_RAP = 2, DANCE = 3, ELECTRONIC = 4, RNB_SOUL = 5, ALTERNATIVE =
                6, ROCK = 7
                LATIN = 8, FILM_TV_STAGE = 9, COUNTRY = 10, AFRO_BEATS = 11, WORLDWIDE = 12,
                REGGAE_DANCE_HALL = 13
                HOUSE = 14, K_POP = 15, FRENCH_POP = 16, SINGER_SONGWRITER = 17,
                REGIONAL_MEXICANO = 18
            :param limit: Determines how many songs the maximum can be in the request.
                Example: If 5 is specified, the query will return no more than 5 songs
            :param offset: A parameter that determines with which song to display the request.
                The default is 0. If you want to skip the first few songs, set this parameter to
                your own.
            :param proxy: Proxy server
            :return: dict songs
        """
        if isinstance(genre, str):
            genre = GenreMusic(genre)

        genre_playlist_id = await self.geo_service.get_genre_from_country(
            country=CountryCode(country_code),
            genre=genre,
        )

        return await self.http_client.request(
            "GET",
            ShazamUrl.TOP_TRACKS_PLAYLIST.format(
                playlist_id=genre_playlist_id,
                language=self.language,
                endpoint_country=self.endpoint_country,
                country_code=country_code,
                limit=limit,
                offset=offset,
            ),
            headers=self.headers(),
            proxy=proxy,
        )

    async def related_tracks(
        self,
        track_id: int,
        limit: int = 20,
        offset: int = 0,
        proxy: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Similar songs based song id
        https://www.shazam.com/track/546891609/2-phu%CC%81t-ho%CC%9Bn-kaiz-remix
            :param track_id: Track number. Example: (549952578)
            https://www.shazam.com/track/549952578/
            :param limit: Determines how many songs the maximum can be in the request.
                Example: If 5 is specified, the query will return no more than 5 songs
            :param offset: A parameter that determines with which song to display the request.
                The default is 0. If you want to skip the first few songs, set this parameter to
                your own.
            :param proxy: Proxy server
            :return: dict tracks
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

    async def search_artist(
        self,
        query: str,
        limit: int = 10,
        offset: int = 0,
        proxy: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Search all artists by prefix or fullname
            :param query: Artist name or search prefix
            :param limit: Determines how many artists the maximum can be in the request.
                Example: If 5 is specified, the query will return no more than 5 artists.
            :param offset: A parameter that determines with which song to display the request.
                The default is 0. If you want to skip the first few songs, set this parameter to
                your own.
            :param proxy: Proxy server
            :return: dict artists
        """
        return await self.http_client.request(
            "GET",
            ShazamUrl.SEARCH_ARTIST.format(
                language=self.language,
                endpoint_country=self.endpoint_country,
                limit=limit,
                offset=offset,
                query=query,
            ),
            headers=self.headers(),
            proxy=proxy,
        )

    async def search_track(
        self,
        query: str,
        limit: int = 10,
        offset: int = 0,
        proxy: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Search all tracks by prefix
            :param query: Track full title or prefix title
            :param limit: Determines how many songs the maximum can be in the request.
                Example: If 5 is specified, the query will return no more than 5 songs.
            :param offset: A parameter that determines with which song to display the request.
                The default is 0. If you want to skip the first few songs, set this parameter to
                your own.
            :param proxy: Proxy server
            :return: dict songs
        """
        return await self.http_client.request(
            "GET",
            ShazamUrl.SEARCH_MUSIC.format(
                language=self.language,
                endpoint_country=self.endpoint_country,
                limit=limit,
                offset=offset,
                query=query,
            ),
            headers=self.headers(),
            proxy=proxy,
        )

    async def listening_counter(
        self,
        track_id: int,
        proxy: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Returns the total track listener counter.
            :param track_id: Track number. Example: (559284007)
            https://www.shazam.com/track/559284007/rampampam
            :param proxy: Proxy server
            :return: The data dictionary that contains the listen counter.
        """

        return await self.http_client.request(
            "GET",
            ShazamUrl.LISTENING_COUNTER.format(
                track_id,
                language=self.language,
            ),
            headers=self.headers(),
            proxy=proxy,
        )

    async def listening_counter_many(
        self,
        track_ids: List[int],
        proxy: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Returns the total track listener counter.
            :param track_ids: Track numbers (list). Example: ([559284007])
            https://www.shazam.com/track/559284007/rampampam
            :param proxy: Proxy server
            :return: The data dictionary that contains the listen counter.
        """
        return await self.http_client.request(
            "GET",
            ShazamUrl.LISTENING_COUNTER_MANY,
            params={"id": track_ids},
            headers=self.headers(),
            proxy=proxy,
        )

    async def artist_albums(
        self,
        artist_id: int,
        limit: int = 10,
        offset: int = 0,
        proxy: Optional[str] = None,
    ):
        """
        Get all albums of a specific artist

          :param artist_id: Artist number. Example (203347991)
          :param limit: Determines how many songs the maximum can be in the request.
              Example: If 5 is specified, the query will return no more than 5 songs.
          :param offset: A parameter that determines with which song to display the request.
              The default is 0. If you want to skip the first few songs, set this parameter to
              your own.
          :param proxy: Proxy server
          :return: dict albums
        """

        return await self.http_client.request(
            "GET",
            ShazamUrl.ARTIST_ALBUMS.format(
                endpoint_country=self.endpoint_country,
                limit=limit,
                offset=offset,
                artist_id=artist_id,
            ),
            headers=self.headers(),
            proxy=proxy,
        )

    async def search_album(
        self,
        album_id: int,
        proxy: Optional[str] = None,
    ):
        """
        Get album info by id

          :param album_id: Album number. Example (203347991)
          :param proxy: Proxy server
          :return: dict albums
        """

        return await self.http_client.request(
            "GET",
            ShazamUrl.ARTIST_ALBUM_INFO.format(
                endpoint_country=self.endpoint_country,
                album_id=album_id,
            ),
            headers=self.headers(),
            proxy=proxy,
        )

    async def get_youtube_data(
        self,
        link: str,
        proxy: Optional[str] = None,
    ) -> Dict[str, Any]:
        return await self.http_client.request(
            "GET",
            link,
            headers=self.headers(),
            proxy=proxy,
        )

    @deprecated("Use recognize method instead of recognize_song")
    async def recognize_song(
        self,
        data: Union[str, pathlib.Path, bytes, bytearray, AudioSegment],
        proxy: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Creating a song signature based on a file and searching for this signature in the shazam
        database.
            :param data: Path to song file or bytes
            :param proxy: Proxy server
            :return: Dictionary with information about the found song
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
        proxy: Optional[str] = None,
    ) -> Dict[str, Any]:
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
                device=Device.random().value,
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
        data: Union[str, bytes, bytearray],
        proxy: Optional[str] = None,
        options: Optional[SearchParams] = None,
    ) -> Dict[str, Any]:
        """
        All logic and mathematics are transferred to RUST lang.

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
            raise ValueError("Invalid data type")

        return await self.send_recognize_request_v2(sig=signature, proxy=proxy)

    async def send_recognize_request_v2(
        self,
        sig: Signature,
        proxy: Optional[str] = None,
    ) -> Dict[str, Any]:
        data = Converter.data_search(
            Request.TIME_ZONE,
            sig.signature.uri,
            sig.signature.samples,
            sig.timestamp,
        )
        return await self.http_client.request(
            "POST",
            ShazamUrl.SEARCH_FROM_FILE.format(
                language=self.language,
                device=Device.random().value,
                endpoint_country=self.endpoint_country,
                uuid_1=str(uuid.uuid4()).upper(),
                uuid_2=str(uuid.uuid4()).upper(),
            ),
            headers=self.headers(),
            proxy=proxy,
            json=data,
        )
