from pathlib import Path
from unittest.mock import AsyncMock

import pytest

from shazamio import HTTPClient, Shazam
from shazamio.misc import Device

_AUDIO = Path(__file__).parents[1] / "examples" / "data" / "Gloria.ogg"


@pytest.mark.parametrize("device", list(Device))
async def test_recognition_profile_only_changes_the_route(device: Device) -> None:
    http = AsyncMock(spec=HTTPClient)
    http.request.return_value = {"matches": []}
    async with Shazam(http_client=http, recognition_device=device) as client:
        await client.recognize(_AUDIO)
    args, kwargs = http.request.call_args
    assert args[0] == "POST"
    assert f"/en-US/GB/{device.value}/-/tag/" in args[1]
    assert kwargs["headers"]["X-Shazam-Platform"] == "IPHONE"
    assert set(kwargs["json"]) == {"timezone", "signature", "timestamp", "context", "geolocation"}


async def test_profile_does_not_change_track_lookup() -> None:
    http = AsyncMock(spec=HTTPClient)
    http.request.return_value = {"matches": []}
    async with Shazam(http_client=http, recognition_device="android") as client:
        await client.track_about("53982678")
    assert "/GB/iphone/-/track/" in http.request.call_args.args[1]
    assert http.request.call_args.kwargs["headers"]["X-Shazam-Platform"] == "IPHONE"


async def test_default_recognition_profile_remains_iphone() -> None:
    http = AsyncMock(spec=HTTPClient)
    http.request.return_value = {"matches": []}
    async with Shazam(http_client=http) as client:
        await client.recognize(_AUDIO)
    assert "/GB/iphone/-/tag/" in http.request.call_args.args[1]


def test_invalid_device_is_rejected() -> None:
    with pytest.raises(ValueError, match="not a valid Device"):
        Shazam(recognition_device="unsupported")
