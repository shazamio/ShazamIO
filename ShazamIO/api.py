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
        self.audio = self.normalize_audio_data(self.songData)

    async def recognize_song(self) -> dict:
        signature_generator = self.create_signature_generator(self.audio)
        while True:
            signature = signature_generator.get_next_signature()
            if not signature:
                break

            results = await self.send_recognize_request(signature)
            return results

    @staticmethod
    async def send_recognize_request(sig: DecodedMessage) -> dict:

        data = Converter.data_search(
            Request.TIME_ZONE,
            sig.encode_to_uri(),
            int(sig.number_samples / sig.sample_rate_hz * 1000),
            int(time.time() * 1000))

        async with aiohttp.ClientSession() as session:
            async with session.post(
                    ShazamUrl.SEARCH_FROM_FILE.format(
                        str(uuid.uuid4()).upper(),
                        str(uuid.uuid4()).upper()),
                    headers=Request.HEADERS, json=data) as resp:
                return await resp.json()
