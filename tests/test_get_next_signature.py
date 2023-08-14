from shazamio.algorithm import SignatureGenerator
from shazamio.signature import DecodedMessage
import random
import pytest


@pytest.fixture
def signature_instance():
    instance = SignatureGenerator()
    instance.input_pending_processing = [
        random.randint(-32768, 32767) for _ in range(128 * 2)
    ]
    return instance


def test_no_samples_to_process(signature_instance):
    signature_instance.samples_processed = len(
        signature_instance.input_pending_processing
    )
    result = signature_instance.get_next_signature()
    assert result is None


def test_successful_signature_extraction(signature_instance):
    result = signature_instance.get_next_signature()
    assert isinstance(result, DecodedMessage)
