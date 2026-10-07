import warnings
from pathlib import Path
from typing import Any, Final

import pytest
from shazamio_core import Signature, SignatureError

from shazamio import SearchParams, Shazam


@pytest.fixture(scope="session")
def song_bytes() -> bytes:
    return Path("examples/data/Gloria.ogg").read_bytes()


@pytest.mark.asyncio
async def test_recognize_file(shazam: Shazam) -> None:
    out = await shazam.recognize(data="examples/data/Gloria.ogg")
    assert out.get("matches") != []
    assert out["track"]["key"] == "53982678"


@pytest.mark.asyncio
async def test_recognize_bytes(song_bytes: bytes, shazam: Shazam) -> None:
    out = await shazam.recognize(data=song_bytes)
    assert out.get("matches") != []
    assert out["track"]["key"] == "53982678"


@pytest.mark.parametrize(
    ("seconds", "match"),
    [
        pytest.param(10, "clients send a 12 s window", id="old-default"),
        pytest.param(14, "clients send a 12 s window", id="below-no-match"),
        pytest.param(15, "returns no matches", id="no-match-floor"),
    ],
)
async def test_a_window_other_than_twelve_warns_at_the_caller(seconds: int, *, match: str) -> None:
    with pytest.warns(UserWarning, match=match) as record:
        shazam = Shazam(segment_duration_seconds=seconds)
    await shazam.close()

    assert record[0].filename == __file__


async def test_the_default_window_does_not_warn() -> None:
    with warnings.catch_warnings():
        warnings.simplefilter("error")
        shazam = Shazam()
    await shazam.close()


async def test_a_window_in_options_warns_at_the_caller(shazam: Shazam) -> None:
    # A missing file fails in the fingerprinting, after the check and before any request.
    with (
        pytest.warns(UserWarning, match="returns no matches") as record,
        pytest.raises(SignatureError),
    ):
        await shazam.recognize(
            "missing.ogg",
            options=SearchParams(segment_duration_seconds=16),
        )

    assert record[0].filename == __file__


def _answer(*, timeskew: float, frequencyskew: float) -> dict[str, Any]:
    return {
        "matches": [{"id": "53982678", "timeskew": timeskew, "frequencyskew": frequencyskew}],
        "track": {"key": "53982678"},
        "tagid": "TAG",
    }


_NO_MATCH: Final[dict[str, Any]] = {"matches": [], "tagid": "TAG"}
_WITHIN: Final[dict[str, Any]] = _answer(
    timeskew=-5e-4,
    frequencyskew=5e-4,
)
_AT_THE_LIMIT: Final[dict[str, Any]] = _answer(
    timeskew=1e-3,
    frequencyskew=0.0,
)
_TIME_BEYOND: Final[dict[str, Any]] = _answer(
    timeskew=-2e-3,
    frequencyskew=0.0,
)
_FREQUENCY_BEYOND: Final[dict[str, Any]] = _answer(
    timeskew=0.0,
    frequencyskew=2e-3,
)
_TEMPO_SHIFTED: Final[dict[str, Any]] = _answer(
    timeskew=2e-2,
    frequencyskew=0.0,
)


def _answer_with(
    monkeypatch: pytest.MonkeyPatch,
    *,
    shazam: Shazam,
    answer: dict[str, Any],
) -> None:
    async def send(sig: Signature, *, proxy: str | None = None) -> dict[str, Any]:
        del sig, proxy  # The answer is fixed; the signature is never sent.
        return answer

    monkeypatch.setattr(shazam, "send_recognize_request_v2", send)


@pytest.mark.parametrize(
    ("answer", "max_skew", "expected"),
    [
        pytest.param(_WITHIN, 1e-3, _WITHIN, id="within"),
        pytest.param(_AT_THE_LIMIT, 1e-3, _AT_THE_LIMIT, id="at-the-limit"),
        pytest.param(_TIME_BEYOND, 1e-3, _NO_MATCH, id="time-beyond"),
        pytest.param(_FREQUENCY_BEYOND, 1e-3, _NO_MATCH, id="frequency-beyond"),
        pytest.param(_TEMPO_SHIFTED, None, _TEMPO_SHIFTED, id="off-by-default"),
        pytest.param(_NO_MATCH, 1e-3, _NO_MATCH, id="no-match"),
    ],
)
async def test_max_skew_rejects_a_skewed_first_match(
    monkeypatch: pytest.MonkeyPatch,
    shazam: Shazam,
    answer: dict[str, Any],
    max_skew: float | None,
    expected: dict[str, Any],
) -> None:
    _answer_with(
        monkeypatch,
        shazam=shazam,
        answer=answer,
    )

    out = await shazam.recognize("examples/data/Gloria.ogg", max_skew=max_skew)

    assert out == expected


@pytest.mark.parametrize(
    "max_skew",
    [
        pytest.param(0.0, id="zero"),
        pytest.param(-1e-3, id="negative"),
        pytest.param(float("nan"), id="nan"),
    ],
)
async def test_max_skew_must_be_positive(shazam: Shazam, max_skew: float) -> None:
    with pytest.raises(ValueError, match="must be above 0"):
        await shazam.recognize("examples/data/Gloria.ogg", max_skew=max_skew)
