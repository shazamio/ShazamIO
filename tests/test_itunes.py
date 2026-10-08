import asyncio
from typing import Any, Final

import pytest

from shazamio import Shazam
from shazamio.exceptions import BadAppleIds, BadParseData
from shazamio.itunes import parse_itunes_track_ids

# Trimmed from a real answer: every song carries far more fields than `trackId`.
_SEARCH_ANSWER: Final[str] = (
    '{"resultCount":2,"results":['
    '{"wrapperType":"track","kind":"song","trackId":697195462,"trackName":"One More Time"},'
    '{"wrapperType":"track","kind":"song","trackId":697402071,"trackName":"One More Time (12 Mix)"}'
    "]}"
)
# Five Apple songs, three of them versions of one Shazam track.
_QUERY_WITH_SHARED_TRACKS: Final[str] = "daft punk one more time"


def test_the_track_ids_are_read_in_apple_order() -> None:
    assert parse_itunes_track_ids(_SEARCH_ANSWER) == [697195462, 697402071]


def test_an_answer_without_results_is_rejected() -> None:
    with pytest.raises(BadParseData):
        parse_itunes_track_ids("<!doctype html>\n")


@pytest.mark.vcr
@pytest.mark.asyncio
async def test_songs_sharing_a_shazam_track_come_back_once(shazam: Shazam) -> None:
    tracks = await shazam.search_tracks_via_itunes(_QUERY_WITH_SHARED_TRACKS)
    track_keys = [track["key"] for track in tracks]

    assert 0 < len(track_keys) < 5
    assert len(set(track_keys)) == len(track_keys)


@pytest.mark.parametrize(
    "limit",
    [
        pytest.param(0, id="zero"),
        pytest.param(201, id="above-apple-maximum"),
    ],
)
@pytest.mark.asyncio
async def test_a_limit_apple_does_not_serve_is_rejected(shazam: Shazam, limit: int) -> None:
    # Apple answers `limit=0` with 20 songs, so without the check this returns tracks.
    with pytest.raises(ValueError, match="limit"):
        await shazam.search_tracks_via_itunes(_QUERY_WITH_SHARED_TRACKS, limit=limit)


async def _search_two_songs(
    url: str,
    *,
    content_type: str,
    params: dict[str, Any],
    proxy: str | None,
) -> str:
    del url, content_type, params, proxy  # Stands in for `request_text`, whose call passes them.
    return _SEARCH_ANSWER


class _FailFirstWaitSecond:
    """Fails the call for the first subject and parks the call for the second."""

    def __init__(self, first: int) -> None:
        self._first = first
        self._cancelled: bool = False

    @property
    def cancelled(self) -> bool:
        return self._cancelled

    async def __call__(self, subject: int) -> None:
        if subject == self._first:
            await asyncio.sleep(0)
            msg: str = "Could not fetch ids"
            raise BadAppleIds(msg)

        try:
            await asyncio.Event().wait()
        except asyncio.CancelledError:
            self._cancelled = True
            raise


@pytest.mark.asyncio
async def test_a_failed_mapping_cancels_the_other_mappings(
    shazam: Shazam,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    call = _FailFirstWaitSecond(first=697195462)

    async def track_keys(apple_ids: list[int], *, proxy: str | None) -> dict[str, str]:
        del proxy  # The method forwards it; the stand-in has no transport.
        await call(apple_ids[0])
        return {}

    monkeypatch.setattr(shazam.http_client, "request_text", _search_two_songs)
    monkeypatch.setattr(shazam, "track_keys_from_apple_ids", track_keys)

    with pytest.raises(BadAppleIds):
        await shazam.search_tracks_via_itunes(_QUERY_WITH_SHARED_TRACKS, limit=2)

    assert call.cancelled


@pytest.mark.asyncio
async def test_a_failed_track_cancels_the_other_tracks(
    shazam: Shazam,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    call = _FailFirstWaitSecond(first=1)
    track_key_by_apple_id: dict[int, str] = {697195462: "1", 697402071: "2"}

    async def track_keys(apple_ids: list[int], *, proxy: str | None) -> dict[str, str]:
        del proxy  # The method forwards it; the stand-in has no transport.
        return {str(apple_ids[0]): track_key_by_apple_id[apple_ids[0]]}

    async def track_about(track_id: int, *, proxy: str | None = None) -> dict[str, Any]:
        del proxy  # The method forwards it; the stand-in has no transport.
        await call(track_id)
        return {}

    monkeypatch.setattr(shazam.http_client, "request_text", _search_two_songs)
    monkeypatch.setattr(shazam, "track_keys_from_apple_ids", track_keys)
    monkeypatch.setattr(shazam, "track_about", track_about)

    with pytest.raises(BadAppleIds):
        await shazam.search_tracks_via_itunes(_QUERY_WITH_SHARED_TRACKS, limit=2)

    assert call.cancelled
