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
        self._locations_cache = None

    async def _get_locations(self):
        """Fetch and cache the locations data."""
        if self._locations_cache is None:
            self._locations_cache = await self.client.request(
                "GET", ShazamUrl.LOCATIONS, "application/json"
            )
        return self._locations_cache

    async def get_country_url_name(self, country: CountryCode) -> str:
        """
        Return the URL-friendly country name from country code.
            :param country: ISO 3166-3 alpha-2 code. Example: RU, NL, ES
            :return: URL name (e.g. 'spain', 'russia')
        """
        data = await self._get_locations()
        for response_country in data["countries"]:
            if country == response_country["id"]:
                return response_country["urlName"]
        raise BadCountryName("Country not found, check country code")

    async def get_city_url_name(self, country: CountryCode, city: str) -> str:
        """
        Return the URL-friendly city name from country code and city name.
            :param country: ISO 3166-3 alpha-2 code
            :param city: City name (e.g. 'Moscow', 'Barcelona')
            :return: URL name (e.g. 'moscow', 'barcelona')
        """
        data = await self._get_locations()
        for response_country in data["countries"]:
            if country == response_country["id"]:
                country_url_name = response_country["urlName"]
                for response_city in response_country["cities"]:
                    if city == response_city["name"]:
                        return f"{country_url_name}/{response_city['urlName']}"
        raise BadCityName("City not found, check city name")

    async def get_genre_url_name(self, genre: GenreMusic) -> str:
        """
        Return the URL-friendly genre name for global genre charts.
            :param genre: Genre enum value
            :return: URL name (e.g. 'rock', 'hip-hop-rap')
        """
        data = await self._get_locations()
        global_data = data.get("global")
        if not global_data:
            raise BadParseData("Global key not found in shazam locations")
        global_genres = global_data.get("genres")
        if not global_genres:
            raise BadParseData("Genres key not found in shazam locations")
        for response_genre in global_genres:
            if genre.value == response_genre["urlName"]:
                return response_genre["urlName"]
        raise BadParseData("Genre not found, check genre name")

    async def get_country_genre_url_name(self, country: CountryCode, genre: GenreMusic) -> str:
        """
        Return URL path for country-specific genre charts.
            :param country: ISO 3166-3 alpha-2 code
            :param genre: Genre enum value
            :return: URL path (e.g. 'spain/hip-hop-rap')
        """
        data = await self._get_locations()
        for response_country in data["countries"]:
            if country == response_country["id"]:
                country_url_name = response_country["urlName"]
                country_genres = response_country.get("genres")
                if not country_genres:
                    raise BadParseData("Genres key not found for this country")
                for response_genre in country_genres:
                    if genre.value == response_genre["urlName"]:
                        return f"{country_url_name}/{response_genre['urlName']}"
        raise BadParseData("Genre not found for this country")

    # Legacy methods kept for backward compatibility
    async def get_country_playlist(self, country: CountryCode) -> str:
        data = await self._get_locations()
        for response_country in data["countries"]:
            if country == response_country["id"]:
                return response_country["listid"]
        raise BadCountryName("Country not found, check country code")

    async def get_city_playlist(self, country: CountryCode, city: str) -> str:
        data = await self._get_locations()
        for response_country in data["countries"]:
            if country == response_country["id"]:
                for response_city in response_country["cities"]:
                    if city == response_city["name"]:
                        return response_city["listid"]
        raise BadCityName("City not found, check city name")

    async def get_genre(self, genre: GenreMusic) -> str:
        data = await self._get_locations()
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
        data = await self._get_locations()
        global_data = data.get("global")
        if not global_data:
            raise BadParseData("Global key not found in shazam locations")
        top = global_data.get("top")
        if not top:
            raise BadParseData("Top key not found in shazam locations")
        return top["listid"]

    async def get_genre_from_country(self, country: CountryCode, genre: GenreMusic) -> str:
        data = await self._get_locations()
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
