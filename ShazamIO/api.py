from aiohttp import ClientRequest

from ShazamIO.converter import Converter
from pydub import AudioSegment
from io import BytesIO
import aiohttp
import uuid
import time

from .algorithm import SignatureGenerator
from .signature import DecodedMessage
from .models import Request, ShazamUrl
from .converter import Converter


class Shazam(Converter):
    def __init__(self, song_data: bytes):
        self.songData = song_data

    @staticmethod
    async def request(method: str, url: str, **kwargs) -> aiohttp.ClientRequest:
        async with aiohttp.ClientSession() as session:
            if method.upper() == 'GET':
                async with session.get(url, **kwargs) as resp:
                    return await resp.json()
            elif method.upper() == 'POST':
                async with session.post(url, **kwargs) as resp:
                    return await resp.json()
            else:
                raise Exception('Wrong method (Accept: GET/POST')

    async def recognize_song(self) -> ClientRequest:
        audio = self.normalize_audio_data(self.songData)
        signature_generator = self.create_signature_generator(audio)
        while True:
            signature = signature_generator.get_next_signature()
            if not signature:
                break

            results = await self.send_recognize_request(signature)
            return results

    async def send_recognize_request(self, sig: DecodedMessage) -> ClientRequest:

        data = Converter.data_search(
            Request.TIME_ZONE,
            sig.encode_to_uri(),
            int(sig.number_samples / sig.sample_rate_hz * 1000),
            int(time.time() * 1000))

        return await self.request('POST',
                                  ShazamUrl.SEARCH_FROM_FILE.format(
                                      str(uuid.uuid4()).upper(),
                                      str(uuid.uuid4()).upper()),
                                  headers=Request.HEADERS, json=data)

    # async def top_world_tracks():
    #     self.r
