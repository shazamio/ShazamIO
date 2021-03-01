import pathlib
import uuid
import time

import typing

from .signature import DecodedMessage
from .models import Request, ShazamUrl
from .enums import GenreMusic
from .converter import Converter, Geo
from .typehints import CountryCode, ShazamResponse
from .utils import load_file


class Shazam(Converter, Geo):
    """Is a asynchronous framework for reverse engineered Shazam API written in Python 3.7 with asyncio and aiohttp."""

    async def top_world_tracks(self,
                               limit: int = 200,
                               start_from: int = 0) -> typing.Union[ShazamResponse, dict]:
        """
        Search top world tracks

            :param limit: Determines how many songs the maximum can be in the request.
                Example: If 5 is specified, the query will return no more than 5 songs.
            :param start_from: A parameter that determines with which song to display the request.
                The default is 0. If you want to skip the first few songs, set this parameter to your own.
            :return: dict tracks
        """
        return await self.request('GET',
                                  ShazamUrl.TOP_TRACKS_WORLD.format(limit, start_from),
                                  headers=Request.HEADERS)

    async def artist_about(self, artist_id: int) -> typing.Union[ShazamResponse, dict]:
        """
        Retrieving information from an artist profile

            :param artist_id: Artist number. Example (203347991) : https://www.shazam.com/artist/203347991/
            :return: dict about artist
        """
        return await self.request('GET',
                                  ShazamUrl.ARTIST_ABOUT.format(artist_id),
                                  headers=Request.HEADERS)

    async def artist_top_tracks(self,
                                artist_id: int,
                                limit: int = 200,
                                start_from: int = 0) -> typing.Union[ShazamResponse, dict]:
        """
        Get the top songs according to Shazam

            :param artist_id: Artist number. Example: (203347991) https://www.shazam.com/artist/203347991/
            :param limit: Determines how many songs the maximum can be in the request.
                Example: If 5 is specified, the query will return no more than 5 songs.
            :param start_from: A parameter that determines with which song to display the request.
                The default is 0. If you want to skip the first few songs, set this parameter to your own.
            :return: dict tracks
        """
        return await self.request('GET',
                                  ShazamUrl.ARTIST_TOP_TRACKS.format(artist_id, start_from, limit),
                                  headers=Request.HEADERS)

    async def track_about(self, track_id: int) -> typing.Union[ShazamResponse, dict]:
        """
        Get track information

            :param track_id: Track number. Example: (549952578) https://www.shazam.com/track/549952578/
            :return: dict about track
        """
        return await self.request('GET',
                                  ShazamUrl.ABOUT_TRACK.format(track_id),
                                  headers=Request.HEADERS)

    async def top_country_tracks(self,
                                 country_code: typing.Union[CountryCode, str],
                                 limit: int = 200,
                                 start_from: int = 0) -> typing.Union[ShazamResponse, dict]:
        """
        Get the best tracks by country code
        https://www.shazam.com/charts/discovery/netherlands

            :param country_code: ISO 3166-3 alpha-2 code. Example: RU,NL,UA
            :param limit: Determines how many songs the maximum can be in the request.
                Example: If 5 is specified, the query will return no more than 5 songs.
            :param start_from: A parameter that determines with which song to display the request.
                The default is 0. If you want to skip the first few songs, set this parameter to your own.
            :return: dict songs
        """
        return await self.request('GET',
                                  ShazamUrl.TOP_TRACKS_COUNTRY.format(country_code, limit, start_from),
                                  headers=Request.HEADERS)

    async def top_city_tracks(self,
                              country_code: typing.Union[CountryCode, str],
                              city_name: str,
                              limit: int = 200,
                              start_from: int = 0) -> typing.Union[ShazamResponse, dict]:

        """
        Retrieving information from an artist profile
        https://www.shazam.com/charts/top-50/russia/moscow

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

    async def top_world_genre_tracks(self,
                                     genre: typing.Union[GenreMusic, int],
                                     limit: int = 100,
                                     start_from: int = 0) -> typing.Union[ShazamResponse, dict]:
        """
        Get world tracks by certain genre
        https://www.shazam.com/charts/genre/world/rock

            :param genre: Genre name or ID:
                POP = 1, HIP_HOP_RAP = 2, DANCE = 3, ELECTRONIC = 4, RNB_SOUL = 5, ALTERNATIVE = 6, ROCK = 7
                LATIN = 8, FILM_TV_STAGE = 9, COUNTRY = 10, AFRO_BEATS = 11, WORLDWIDE = 12, REGGAE_DANCE_HALL = 13
                HOUSE = 14, K_POP = 15, FRENCH_POP = 16, SINGER_SONGWRITER = 17, REGIONAL_MEXICANO = 18

            :param limit: Determines how many songs the maximum can be in the request.
                    Example: If 5 is specified, the query will return no more than 5 songs.
            :param start_from: A parameter that determines with which song to display the request.
                    The default is 0. If you want to skip the first few songs, set this parameter to your own.
            :return: dict songs
        """
        return await self.request('GET',
                                  ShazamUrl.GENRE_WORLD.format(genre, limit, start_from),
                                  headers=Request.HEADERS)

    async def top_country_genre_tracks(self,
                                       country_code: str,
                                       genre: typing.Union[GenreMusic, int],
                                       limit: int = 200,
                                       start_from: int = 0) -> typing.Union[ShazamResponse, dict]:
        """
        The best tracks by a genre in the country
        https://www.shazam.com/charts/genre/spain/hip-hop-rap

            :param country_code: ISO 3166-3 alpha-2 code. Example: RU,NL,UA
            :param genre: Genre name or ID:
                POP = 1, HIP_HOP_RAP = 2, DANCE = 3, ELECTRONIC = 4, RNB_SOUL = 5, ALTERNATIVE = 6, ROCK = 7
                LATIN = 8, FILM_TV_STAGE = 9, COUNTRY = 10, AFRO_BEATS = 11, WORLDWIDE = 12, REGGAE_DANCE_HALL = 13
                HOUSE = 14, K_POP = 15, FRENCH_POP = 16, SINGER_SONGWRITER = 17, REGIONAL_MEXICANO = 18
            :param limit: Determines how many songs the maximum can be in the request.
                Example: If 5 is specified, the query will return no more than 5 songs.
            :param start_from: A parameter that determines with which song to display the request.
                The default is 0. If you want to skip the first few songs, set this parameter to your own.
            :return: dict songs
        """
        return await self.request('GET',
                                  ShazamUrl.GENRE_COUNTRY.format(country_code, genre, limit, start_from),
                                  headers=Request.HEADERS)

    async def related_tracks(self,
                             track_id: int,
                             limit: int = 20,
                             start_from: int = 0) -> typing.Union[ShazamResponse, dict]:
        """
        Similar songs based song id
        https://www.shazam.com/track/546891609/2-phu%CC%81t-ho%CC%9Bn-kaiz-remix

            :param track_id: Track number. Example: (549952578) https://www.shazam.com/track/549952578/
            :param limit: Determines how many songs the maximum can be in the request.
                Example: If 5 is specified, the query will return no more than 5 songs.
            :param start_from: A parameter that determines with which song to display the request.
                The default is 0. If you want to skip the first few songs, set this parameter to your own.
            :return: dict tracks
        """
        return await self.request('GET',
                                  ShazamUrl.RELATED_SONGS.format(track_id, start_from, limit),
                                  headers=Request.HEADERS)

    async def search_artist(self,
                            query: str,
                            limit: int = 10) -> typing.Union[ShazamResponse, dict]:
        """
        Search all artists by prefix or fullname

            :param query: Artist name or search prefix
            :param limit: Determines how many artists the maximum can be in the request.
                Example: If 5 is specified, the query will return no more than 5 artists.
            :return: dict artists
        """
        return await self.request('GET',
                                  ShazamUrl.SEARCH_ARTIST.format(query, limit),
                                  headers=Request.HEADERS)

    async def search_track(self,
                           query: str,
                           limit: int = 10) -> typing.Union[ShazamResponse, dict]:
        """
        Search all tracks by prefix
            :param query: Track full title or prefix title
            :param limit: Determines how many songs the maximum can be in the request.
                Example: If 5 is specified, the query will return no more than 5 songs.
            :return: dict songs
        """
        return await self.request('GET',
                                  ShazamUrl.SEARCH_MUSIC.format(query, limit),
                                  headers=Request.HEADERS)

    async def recognize_song(self, file_path: typing.Union[str, pathlib.Path]) -> typing.Union[ShazamResponse, dict]:
        """
        Creating a song signature based on a file and searching for this signature in the shazam database.

            :param file_path: Path to song file
            :return: Dictionary with information about the found song
        """
        file = await load_file(file_path, 'rb')
        audio = self.normalize_audio_data(file)
        signature_generator = self.create_signature_generator(audio)
        signature = signature_generator.get_next_signature()
        while not signature:
            signature = signature_generator.get_next_signature()
        results = await self.send_recognize_request(signature)
        return results

    async def send_recognize_request(self, sig: DecodedMessage) -> typing.Union[ShazamResponse, dict]:

        data = Converter.data_search(Request.TIME_ZONE,
                                     sig.encode_to_uri(),
                                     int(sig.number_samples / sig.sample_rate_hz * 1000),
                                     int(time.time() * 1000))

        return await self.request('POST',
                                  ShazamUrl.SEARCH_FROM_FILE.format(
                                      str(uuid.uuid4()).upper(),
                                      str(uuid.uuid4()).upper()),
                                  headers=Request.HEADERS, json=data)
