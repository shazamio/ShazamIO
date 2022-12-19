from pydub import AudioSegment
from shazamio.algorithm import SignatureGenerator
from shazamio.client import HTTPClient
from shazamio.exceptions import BadCityName, BadCountryName
from shazamio.misc import ShazamUrl
from shazamio.schemas.models import *
from shazamio.typehints import CountryCode


class Geo(HTTPClient):
    async def city_id_from(self, country: Union[CountryCode, str], city: str) -> int:
        """
        Return City ID from country name and city name.
            :param country: - Country name
            :param city: - City name
            :return: City ID
        """

        data = await self.request("GET", ShazamUrl.CITY_IDS, "text/plain")
        for response_country in data["countries"]:
            if country == response_country["id"]:
                for response_city in response_country["cities"]:
                    if city == response_city["name"]:
                        return response_city["id"]
        raise BadCityName("City not found, check city name")

    async def all_cities_from_country(self, country: Union[CountryCode, str]) -> list:
        cities = []
        data = await self.request("GET", ShazamUrl.CITY_IDS, "text/plain")
        for response_country in data["countries"]:
            if country == response_country["id"]:
                for city in response_country["cities"]:
                    cities.append(city["name"])
                return cities
        raise BadCountryName("Country not found, check country name")


class Converter:
    @staticmethod
    def data_search(timezone: str, uri: str, samplems: int, timestamp: int) -> dict:
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
