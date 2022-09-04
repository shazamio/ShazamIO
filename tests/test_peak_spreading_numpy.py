from pydub import AudioSegment
from typing import List

from shazamio.algorithm import SignatureGenerator
from types import MethodType


def do_peak_spreading_non_numpy(self):
    origin_last_fft: List[float] = self.fft_outputs[self.fft_outputs.position - 1]

    spread_last_fft: List[float] = list(origin_last_fft)

    for position in range(1025):

        # Perform frequency-domain spreading of peak values

        if position < 1023:
            spread_last_fft[position] = max(spread_last_fft[position : position + 3])

        # Perform time-domain spreading of peak values

        max_value = spread_last_fft[position]

        for former_fft_num in [-1, -3, -6]:
            former_fft_output = self.spread_fft_output[
                (self.spread_fft_output.position + former_fft_num)
                % self.spread_fft_output.buffer_size
            ]

            former_fft_output[position] = max_value = max(
                former_fft_output[position], max_value
            )

    # Save output locally

    self.spread_fft_output.append(spread_last_fft)

    pass


async def test_do_peak_spreading_numpy():
    audio = AudioSegment.from_file(file="examples/data/dora.ogg")

    audio = audio.set_sample_width(2)
    audio = audio.set_frame_rate(16000)
    audio = audio.set_channels(1)

    signature_generator_non_numpy = SignatureGenerator()
    signature_generator_non_numpy.do_peak_spreading = MethodType(
        do_peak_spreading_non_numpy, signature_generator_non_numpy
    )
    signature_generator_non_numpy.feed_input(audio.get_array_of_samples())
    signature_generator_non_numpy.MAX_TIME_SECONDS = 12

    signature_non_numpy = signature_generator_non_numpy.get_next_signature()

    while not signature_non_numpy:
        signature_non_numpy = signature_generator_non_numpy.get_next_signature()

    signature_generator = SignatureGenerator()
    signature_generator.feed_input(audio.get_array_of_samples())
    signature_generator.MAX_TIME_SECONDS = 12

    signature = signature_generator.get_next_signature()

    while not signature:
        signature = signature_generator.get_next_signature()
    print(type(signature.encode_to_binary()))
    print(type(signature_non_numpy.encode_to_binary()))
    assert signature.encode_to_binary() == signature_non_numpy.encode_to_binary()
