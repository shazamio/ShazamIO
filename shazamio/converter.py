from typing import Any

from pydub import AudioSegment

from shazamio.algorithm import SignatureGenerator


class Converter:
    @staticmethod
    def data_search(timezone: str, uri: str, samplems: int, timestamp: int) -> dict[str, Any]:
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
        return audio.set_channels(1)

    @staticmethod
    def create_signature_generator(audio: AudioSegment) -> SignatureGenerator:
        signature_generator = SignatureGenerator()
        signature_generator.feed_input(audio.get_array_of_samples())
        signature_generator.MAX_TIME_SECONDS = 12
        if audio.duration_seconds > 12 * 3:
            signature_generator.samples_processed += 16000 * (int(audio.duration_seconds / 2) - 6)
        return signature_generator
