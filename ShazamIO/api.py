from ShazamIO.converter import Converter
from pydub import AudioSegment
from io import BytesIO
import aiohttp
import uuid
import time

from .algorithm import SignatureGenerator
from .signature import DecodedMessage
from .models import Request, ShazamUrl


class Shazam:
    def __init__(self, song_data: bytes):
        self.songData = song_data
        self.audio = self.normalize_audio_data(self.songData)
        self.MAX_TIME_SECONDS = 8

    async def recognize_song(self) -> dict:
        signature_generator = self.createSignatureGenerator(self.audio)
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

    @staticmethod
    def normalize_audio_data(song_data: bytes) -> AudioSegment:

        audio = AudioSegment.from_file(BytesIO(song_data))
        audio = audio.set_sample_width(2)
        audio = audio.set_frame_rate(16000)
        audio = audio.set_channels(1)

        return audio

    def createSignatureGenerator(self, audio: AudioSegment) -> SignatureGenerator:
        signature_generator = SignatureGenerator()
        signature_generator.feed_input(audio.get_array_of_samples())
        signature_generator.MAX_TIME_SECONDS = self.MAX_TIME_SECONDS
        if audio.duration_seconds > 12 * 3:
            signature_generator.samples_processed += 16000 * (int(audio.duration_seconds / 16) - 6)
        return signature_generator
