import pathlib
import uuid
import time

import typing

from .signature import DecodedMessage
from .models import Request, ShazamUrl, GenreMusic
from .converter import Converter
from .client import HTTPClient
from .utils import load_file


class Shazam(Converter, HTTPClient):

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

    async def top_city_tracks(self, city_id: int, limit: int = 200, start_from: int = 0) -> dict:
        return await self.request('GET', ShazamUrl.TOP_TRACKS_CITY.format(city_id, limit, start_from),
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
        audio = await self.normalize_audio_data(file)
        signature_generator = await self.create_signature_generator(audio)
        signature = await signature_generator.get_next_signature()
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
