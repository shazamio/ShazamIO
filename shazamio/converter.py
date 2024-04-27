from typing import Any, Dict

from pydub import AudioSegment

from shazamio.enums import GenreMusic
from shazamio.algorithm import SignatureGenerator
from shazamio.exceptions import BadCityName, BadCountryName, BadParseData
from shazamio.interfaces.client import HTTPClientInterface
from shazamio.misc import ShazamUrl
from shazamio.typehints import CountryCode


class GeoService:
    def __init__(self, client: HTTPClientInterface):
        self.client = client

    async def get_country_playlist(self, country: CountryCode) -> str:
        """
        Return Country playlistID from country name
            :param country: - Country code, format: ISO 3166-3 alpha-2 code. Example: RU,NL,UA
            :return: City ID
        """

        data = await self.client.request("GET", ShazamUrl.LOCATIONS, "application/json")
        for response_country in data["countries"]:
            if country == response_country["id"]:
                return response_country["listid"]
        raise BadCountryName("Country not found, check city name")

    async def get_city_playlist(self, country: CountryCode, city: str) -> str:
        """
        Return playlistID from country name and city name.
            :param country: - Country name
            :param city: - City name
            :return: City ID
        """

        data = await self.client.request("GET", ShazamUrl.LOCATIONS, "application/json")
        for response_country in data["countries"]:
            if country == response_country["id"]:
                for response_city in response_country["cities"]:
                    if city == response_city["name"]:
                        return response_city["listid"]
        raise BadCityName("City not found, check city name")

    async def get_genre(self, genre: GenreMusic) -> str:
        """
        Return Global Genre playlistID from country name and city name.
            :param genre: - Genre urlName from https://www.shazam.com/services/charts/locations
            :return: City ID
        """

        data = await self.client.request("GET", ShazamUrl.LOCATIONS, "application/json")
        global_data = data.get("global")
        if not global_data:
            raise BadParseData("Global key not found in shazam locations")

        global_genres = global_data.get("genres")
        if not global_genres:
            raise BadParseData("Genres key not found in shazam locations")

        for response_genre in global_genres:
            if genre.value == response_genre["urlName"]:
                return response_genre["listid"]

        raise BadCityName("Genre not found, check genre name")

    async def get_top(self) -> str:
        data = await self.client.request("GET", ShazamUrl.LOCATIONS, "application/json")
        global_data = data.get("global")
        if not global_data:
            raise BadParseData("Global key not found in shazam locations")

        top = global_data.get("top")
        if not top:
            raise BadParseData("Top key not found in shazam locations")
        return top["listid"]

    async def get_genre_from_country(self, country: CountryCode, genre: GenreMusic) -> str:
        """
        Return Global Genre playlistID from country name and genre urlName from https://www.shazam.com/services/charts/locations
            :param country: - Country code, format: ISO 3166-3 alpha-2 code. Example: RU,NL,UA
            :param genre: - Genre urlName from https://www.shazam.com/services/charts/locations
            :return: City ID
        """

        data = await self.client.request("GET", ShazamUrl.LOCATIONS, "application/json")
        for response_country in data["countries"]:
            if country == response_country["id"]:
                global_genres = response_country.get("genres")
                if not global_genres:
                    raise BadParseData("Genres key not found in shazam locations")

                for response_genre in global_genres:
                    if genre.value == response_genre["urlName"]:
                        return response_genre["listid"]

        raise BadCityName("Genre not found, check genre name")


class Converter:
    @staticmethod
    def data_search(timezone: str, uri: str, samplems: int, timestamp: int) -> Dict[str, Any]:
        return {
            "timezone": timezone,
            "signature": {"uri": uri, "samplems": samplems},
            "timestamp": timestamp,
            "context": {},
            "geolocation": {},
        }

    @staticmethod
    def normalize_audio_data(audio: AudioSegment) -> AudioSegment:
        audio = audio.set_sample_width(2)
        audio = audio.set_frame_rate(16000)
        audio = audio.set_channels(1)

        return audio

    @staticmethod
    def create_signature_generator(audio: AudioSegment) -> SignatureGenerator:
        signature_generator = SignatureGenerator()
        signature_generator.feed_input(audio.get_array_of_samples())
        signature_generator.MAX_TIME_SECONDS = 12
        if audio.duration_seconds > 12 * 3:
            signature_generator.samples_processed += 16000 * (int(audio.duration_seconds / 2) - 6)
        return signature_generator
