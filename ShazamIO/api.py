import pathlib
import uuid
import time

import typing

from .signature import DecodedMessage
from .models import Request, ShazamUrl, GenreMusic
from .converter import Converter, Geo
from .typehints import CountryCode, ShazamResponse
from .utils import load_file


class Shazam(Converter, Geo):
    """Is a asynchronous framework for reverse engineered Shazam API written in Python 3.7 with asyncio and aiohttp."""

    async def top_world_tracks(self, limit: int = 200, start_from: int = 0) -> dict:
        return await self.request('GET', ShazamUrl.TOP_TRACKS_WORLD.format(limit, start_from), headers=Request.HEADERS)

    async def artist_about(self, artist_id: int):
        return await self.request('GET', ShazamUrl.ARTIST_ABOUT.format(artist_id))

    async def artist_top_tracks(self, artist_id: int, limit: int = 200, start_from: int = 0) -> dict:
        return await self.request('GET', ShazamUrl.ARTIST_TOP_TRACKS.format(artist_id, start_from, limit),
                                  headers=Request.HEADERS)

    async def track_about(self, track_id: int) -> dict:
        return await self.request('GET', ShazamUrl.ABOUT_TRACK.format(track_id), headers=Request.HEADERS)

    async def top_country_tracks(self, country: str, limit: int = 200, start_from: int = 0):
        return await self.request('GET', ShazamUrl.TOP_TRACKS_COUNTRY.format(country, limit, start_from),
                                  headers=Request.HEADERS)

    async def top_city_tracks(self, country_code: typing.Union[CountryCode, str],
                              city_name: str, limit: int = 200,
                              start_from: int = 0) -> typing.Union[ShazamResponse, dict]:

        """
            :param country_code: ISO 3166-3 alpha-2 code. Example: RU,NL,UA
            :param city_name: City name from https://github.com/dotX12/dotX12/blob/main/city.json
                Example: Budapest, Moscow
            :param limit: Determines how many songs the maximum can be in the request.
                Example: If 5 is specified, the query will return no more than 5 songs.
            :param start_from: A parameter that determines with which song to display the request.
                The default is 0. If you want to skip the first few songs, set this parameter to your own.
            :return: dict songs
        """
        city_id = await Geo(country_code, city_name).city_id_from()
        return await self.request('GET',
                                  ShazamUrl.TOP_TRACKS_CITY.format(city_id, limit, start_from),
                                  headers=Request.HEADERS)

    async def top_world_genre_tracks(self, genre: typing.Union[GenreMusic, int], limit: int = 100,
                                     start_from: int = 0) -> dict:
        return await self.request('GET', ShazamUrl.GENRE_WORLD.format(genre, limit, start_from),
                                  headers=Request.HEADERS)

    async def top_country_genre_tracks(self, country: str, genre: typing.Union[GenreMusic, int], limit: int = 200,
                                       start_from: int = 0) -> dict:
        return await self.request('GET', ShazamUrl.GENRE_COUNTRY.format(country, genre, limit, start_from),
                                  headers=Request.HEADERS)

    async def related_tracks(self, track_id: int, limit: int = 20, start_from: int = 0) -> dict:
        return await self.request('GET', ShazamUrl.RELATED_SONGS.format(track_id, start_from, limit),
                                  headers=Request.HEADERS)

    async def search_artist(self, query: str, limit: int = 10) -> dict:
        return await self.request('GET', ShazamUrl.SEARCH_ARTIST.format(query, limit), headers=Request.HEADERS)

    async def search_track(self, query: str, limit: int = 10) -> dict:
        return await self.request('GET', ShazamUrl.SEARCH_MUSIC.format(query, limit), headers=Request.HEADERS)

    async def recognize_song(self, file_path: typing.Union[str, pathlib.Path]) -> dict:
        file = await load_file(file_path, 'rb')
        audio = self.normalize_audio_data(file)
        signature_generator = self.create_signature_generator(audio)
        signature = signature_generator.get_next_signature()
        while not signature:
            signature = signature_generator.get_next_signature()
        results = await self.send_recognize_request(signature)
        return results

    async def send_recognize_request(self, sig: DecodedMessage) -> dict:
        data = Converter.data_search(Request.TIME_ZONE, sig.encode_to_uri(),
                                     int(sig.number_samples / sig.sample_rate_hz * 1000), int(time.time() * 1000))

        return await self.request('POST', ShazamUrl.SEARCH_FROM_FILE.format(
            str(uuid.uuid4()).upper(),
            str(uuid.uuid4()).upper()),
                                  headers=Request.HEADERS, json=data)
