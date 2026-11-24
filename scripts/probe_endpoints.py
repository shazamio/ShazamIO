"""Run every public `Shazam` method against the live service and report what it answered.

A diagnostic, not a test: it talks to a live third-party service, so nothing in CI
runs it. Run it with `just probe` before a release, or when a user reports an
empty result, and read the verdict column.
"""

import asyncio
import enum
import inspect
import sys
from collections.abc import Awaitable, Sequence
from dataclasses import dataclass
from http import HTTPStatus
from pathlib import Path
from typing import Final, Protocol

from shazamio_core import Recognizer

from shazamio import (
    AiohttpTransport,
    ChartTrack,
    GenreMusic,
    Request,
    Response,
    ResponseTrack,
    Shazam,
    ShazamError,
    TrackInfo,
    Transport,
    YoutubeData,
)

_LANGUAGE: Final[str] = "en-US"
_COUNTRY: Final[str] = "GB"
_SAMPLE: Final[Path] = Path(__file__).parent.parent / "examples" / "data" / "Gloria.ogg"
_SHOWN_CHARACTERS: Final[int] = 60
_SHOWN_ERROR_CHARACTERS: Final[int] = 200
_NOT_PROBED: Final[frozenset[str]] = frozenset({"close"})

# Sample inputs that resolve live. One that stops resolving shows up
#  as `UNEXPECTED` on its own row, not as a dead endpoint.
_TRACK_ID: Final[int] = 549952578
_APPLE_ID: Final[int] = 1125281672
_CHART_COUNTRY: Final[str] = "RU"
_CHART_CITY: Final[str] = "Moscow"
_SEARCH_TERM: Final[str] = "adele"


class Verdict(enum.Enum):
    LIVE = "LIVE"
    DEAD = "DEAD"
    BAD_INPUT = "BAD_INPUT"
    UNEXPECTED = "UNEXPECTED"


class Call(Protocol):
    def __call__(
        self,
        shazam: Shazam,
        /,
    ) -> Awaitable[
        ResponseTrack
        | TrackInfo
        | YoutubeData
        | dict[str, str]
        | list[TrackInfo]
        | list[ChartTrack]
    ]:
        """Call one public method of `shazam`."""


@dataclass(frozen=True, slots=True)
class Probe:
    method: str
    label: str
    call: Call
    expected: Verdict = Verdict.LIVE


@dataclass(frozen=True, slots=True)
class Exchange:
    request: Request
    response: Response


@dataclass(frozen=True, slots=True)
class Outcome:
    exchanges: Sequence[Exchange]
    error: ShazamError | None


class _Recorder(Transport):
    """Keeps every raw answer, before `Shazam` checks it."""

    def __init__(self, inner: Transport) -> None:
        self._inner = inner
        self._exchanges: list[Exchange] = []

    @property
    def exchanges(self) -> Sequence[Exchange]:
        return self._exchanges

    async def send(self, request: Request) -> Response:
        response = await self._inner.send(request)

        exchange = Exchange(
            request=request,
            response=response,
        )
        self._exchanges.append(exchange)

        return response

    async def close(self) -> None:
        """The inner transport is closed by whoever opened it."""


async def _youtube_of_a_track(shazam: Shazam) -> YoutubeData:
    track = await shazam.track_about(_TRACK_ID)

    if track.youtube_link is None:
        msg: str = f"track {_TRACK_ID} carries no YouTube link"
        raise ShazamError(msg)

    return await shazam.get_youtube_data(track.youtube_link)


async def _recognize_a_signature(shazam: Shazam) -> ResponseTrack:
    signature = await Recognizer().recognize_path(value=str(_SAMPLE))

    return await shazam.recognize_signature(signature)


def probes() -> list[Probe]:
    return [
        Probe(
            method=Shazam.recognize.__name__,
            label="recognize(Gloria.ogg)",
            call=lambda shazam: shazam.recognize(_SAMPLE),
        ),
        Probe(
            method=Shazam.recognize_signature.__name__,
            label="recognize_signature(Gloria.ogg)",
            call=_recognize_a_signature,
        ),
        Probe(
            method=Shazam.track_about.__name__,
            label=f"track_about({_TRACK_ID})",
            call=lambda shazam: shazam.track_about(_TRACK_ID),
        ),
        Probe(
            method=Shazam.get_youtube_data.__name__,
            label=f"get_youtube_data(track {_TRACK_ID})",
            call=_youtube_of_a_track,
        ),
        Probe(
            method=Shazam.track_keys_from_apple_ids.__name__,
            label=f"track_keys_from_apple_ids([{_APPLE_ID}])",
            call=lambda shazam: shazam.track_keys_from_apple_ids([_APPLE_ID]),
        ),
        Probe(
            method=Shazam.search_tracks_via_itunes.__name__,
            label=f"search_tracks_via_itunes({_SEARCH_TERM!r}, limit=1)",
            call=lambda shazam: shazam.search_tracks_via_itunes(_SEARCH_TERM, limit=1),
        ),
        Probe(
            method=Shazam.top_tracks.__name__,
            label="top_tracks()",
            call=lambda shazam: shazam.top_tracks(),
        ),
        Probe(
            method=Shazam.top_tracks.__name__,
            label="top_tracks(genre=pop)",
            call=lambda shazam: shazam.top_tracks(genre=GenreMusic.POP),
        ),
        Probe(
            method=Shazam.top_tracks.__name__,
            label=f"top_tracks({_CHART_COUNTRY!r})",
            call=lambda shazam: shazam.top_tracks(_CHART_COUNTRY),
        ),
        Probe(
            method=Shazam.top_tracks.__name__,
            label=f"top_tracks({_CHART_COUNTRY!r}, genre=pop)",
            call=lambda shazam: shazam.top_tracks(_CHART_COUNTRY, genre=GenreMusic.POP),
        ),
        Probe(
            method=Shazam.top_tracks.__name__,
            label=f"top_tracks({_CHART_COUNTRY!r}, city={_CHART_CITY!r})",
            call=lambda shazam: shazam.top_tracks(_CHART_COUNTRY, city=_CHART_CITY),
        ),
        # A genre the country does not offer is a clean empty `404`, which is the
        #  service working.
        Probe(
            method=Shazam.top_tracks.__name__,
            label=f"top_tracks({_CHART_COUNTRY!r}, genre=rock)",
            call=lambda shazam: shazam.top_tracks(_CHART_COUNTRY, genre=GenreMusic.ROCK),
            expected=Verdict.BAD_INPUT,
        ),
    ]


def unprobed_methods(checked: list[Probe]) -> set[str]:
    declared = {
        name
        for name, _member in inspect.getmembers(Shazam, inspect.iscoroutinefunction)
        if not name.startswith("_")
    }

    return declared - _NOT_PROBED - {probe.method for probe in checked}


def classify(
    probe: Probe,
    *,
    outcome: Outcome,
) -> Verdict:
    last = outcome.exchanges[-1].response if outcome.exchanges else None

    # A retired path answers the website instead, often as `200 text/html`.
    if last is not None and last.content_type == "text/html":
        return Verdict.DEAD

    if probe.expected is Verdict.BAD_INPUT:
        is_clean_miss: bool = (
            last is not None and last.status == HTTPStatus.NOT_FOUND and not last.text
        )
        return Verdict.BAD_INPUT if is_clean_miss else Verdict.UNEXPECTED

    if outcome.error is not None:
        return Verdict.UNEXPECTED

    return Verdict.LIVE


async def _run(
    probe: Probe,
    *,
    transport: Transport,
) -> Outcome:
    recorder = _Recorder(transport)
    shazam = Shazam(
        language=_LANGUAGE,
        country=_COUNTRY,
        transport=recorder,
        retry=None,
    )

    try:
        await probe.call(shazam)
    except ShazamError as er:
        return Outcome(
            exchanges=recorder.exchanges,
            error=er,
        )

    return Outcome(
        exchanges=recorder.exchanges,
        error=None,
    )


def _report_line(
    probe: Probe,
    *,
    outcome: Outcome,
    verdict: Verdict,
) -> str:
    marker = "  " if verdict is probe.expected else "!!"
    lines = [f"{marker} {verdict.value:<10} {probe.label}"]

    for exchange in outcome.exchanges:
        response = exchange.response
        line = (
            f"{'':14}{response.status} {response.content_type:<25} "
            f"{len(response.text):>9} chars  {exchange.request.url}"
        )
        lines.append(line)

    if outcome.error is not None:
        lines.append(
            f"{'':14}{type(outcome.error).__name__}: {outcome.error!s:.{_SHOWN_ERROR_CHARACTERS}}"
        )
    elif outcome.exchanges:
        shown = outcome.exchanges[-1].response.text[:_SHOWN_CHARACTERS]
        lines.append(f"{'':14}{shown!r}")

    return "\n".join(lines)


async def main() -> int:
    all_probes = probes()
    unprobed = unprobed_methods(all_probes)

    if unprobed:
        print(f"no probe for Shazam.{', Shazam.'.join(sorted(unprobed))}", file=sys.stderr)
        return 2

    surprises: int = 0
    transport = AiohttpTransport()

    # Serially: parallel requests to `www.` make live paths answer the website.
    try:
        for probe in all_probes:
            outcome = await _run(probe, transport=transport)
            verdict = classify(probe, outcome=outcome)
            surprises += verdict is not probe.expected

            print(
                _report_line(
                    probe,
                    outcome=outcome,
                    verdict=verdict,
                ),
            )
    finally:
        await transport.close()

    print(f"\n{len(all_probes)} probed, {surprises} not as expected (marked !!)")
    return 1 if surprises else 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
