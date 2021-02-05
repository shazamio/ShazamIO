from io import BytesIO

from pydub import AudioSegment

from ShazamIO.algorithm import SignatureGenerator
from ShazamIO.client import HTTPClient
from ShazamIO.exceptions import BadCityName, BadCountryName
from ShazamIO.models import *


class AboutTrack:
    def __init__(self, track: dict):
        self.track = track['track'] if 'timezone' in track else track
        self.track_id = self.track['key']
        self.title = self.track['title']
        self.author = self.track['subtitle']
        self.photo_url = self.track['images']['coverarthq'] if 'images' in self.track else None
        self.ringtone_url = self.track['hub']['actions'][1]['uri'] if 'actions' in self.track['hub'] else None
        self.artist_id = self.track['artists'][0]['id'] if 'artists' in self.track else None
        self.shazam_url = f'https://www.shazam.com/track/{self.track_id}'

    def __str__(self):
        return (f'Author: {self.author} - {self.title}\n'
                f'Artist ID: {self.artist_id}'
                f'Shazam URL: {self.shazam_url}\n'
                f'Ringtone: {self.ringtone_url}\n'
                f'Track photo: {self.photo_url}\n')


class Geo(HTTPClient):

    async def city_id_from(self, country: str, city: str) -> int:
        data = await self.request('GET', ShazamUrl.CITY_IDs, 'text/plain')
        for response_country in data['countries']:
            if country == response_country['id']:
                for response_city in response_country['cities']:
                    if city == response_city['name']:
                        return response_city['id']
        raise BadCityName('City not found, check city name')

    async def all_cities_from_country(self, country: str) -> list:
        cities = []
        data = await self.request('GET', ShazamUrl.CITY_IDs, 'text/plain')
        for response_country in data['countries']:
            if country == response_country['id']:
                for city in response_country['cities']:
                    cities.append(city['name'])
                return cities
        raise BadCountryName('Country not found, check country name')


class Converter:

    @staticmethod
    def data_search(timezone: str, uri: str, samplems: int, timestamp: int) -> dict:
        return {'timezone': timezone, 'signature': {'uri': uri, 'samplems': samplems},
                'timestamp': timestamp, 'context': {}, 'geolocation': {}}

    @staticmethod
    def normalize_audio_data(song_data: bytes) -> AudioSegment:

        audio = AudioSegment.from_file(BytesIO(song_data))
        audio = audio.set_sample_width(2)
        audio = audio.set_frame_rate(16000)
        audio = audio.set_channels(1)

        return audio

    @staticmethod
    def create_signature_generator(audio: AudioSegment) -> SignatureGenerator:
        signature_generator = SignatureGenerator()
        signature_generator.feed_input(audio.get_array_of_samples())
        signature_generator.MAX_TIME_SECONDS = 8
        if audio.duration_seconds > 12 * 3:
            signature_generator.samples_processed += 16000 * (int(audio.duration_seconds / 16) - 6)
        return signature_generator
