"""Ask every URL the library calls what it answers, one request at a time.

A diagnostic, not a test: it talks to a live third-party service, so nothing in CI
runs it. Run it with `just probe` before a release, or when a user reports an
empty result, and read the verdict column.
"""

import asyncio
import enum
import json
import sys
import uuid
from dataclasses import dataclass
from http import HTTPStatus
from pathlib import Path
from typing import Any, Final
from urllib.parse import urlencode

import aiohttp
from shazamio_core import Recognizer

from shazamio.apple import APPLE_TO_SHAZAM_CONTENT_TYPE
from shazamio.charts import CHART_CONTENT_TYPE
from shazamio.converter import Converter
from shazamio.itunes import ITUNES_SEARCH_CONTENT_TYPE
from shazamio.misc import Device, Request, ShazamUrl

_LANGUAGE: Final[str] = "en-US"
_ENDPOINT_COUNTRY: Final[str] = "GB"
_JSON_CONTENT_TYPE: Final[str] = "application/json"
_SAMPLE: Final[Path] = Path(__file__).parent.parent / "examples" / "data" / "Gloria.ogg"
_SHOWN_BYTES: Final[int] = 60

# Sample inputs known to resolve on 2026-10-06. One that stops resolving shows up
#  as `UNEXPECTED` on its own row, not as a dead endpoint.
_TRACK_ID: Final[int] = 549952578
_APPLE_ID: Final[int] = 1125281672
_COUNTRY_SLUG: Final[str] = "russia"
_CITY_SLUG: Final[str] = "moscow"
_GENRE_SLUG: Final[str] = "pop"
_SEARCH_TERM: Final[str] = "adele"


class Verdict(enum.Enum):
    LIVE = "LIVE"
    DEAD = "DEAD"
    BAD_INPUT = "BAD_INPUT"
    UNEXPECTED = "UNEXPECTED"


@dataclass(frozen=True, slots=True)
class Probe:
    url_name: str
    url: str
    content_type: str
    expected: Verdict = Verdict.LIVE


@dataclass(frozen=True, slots=True)
class Answer:
    status: int
    content_type: str
    body: bytes


def _chart(url_name: str, *, url: str, expected: Verdict = Verdict.LIVE) -> Probe:
    return Probe(
        url_name=url_name,
        url=url,
        content_type=CHART_CONTENT_TYPE,
        expected=expected,
    )


def probes() -> list[Probe]:
    return [
        Probe(
            url_name="SEARCH_FROM_FILE",
            url=ShazamUrl.SEARCH_FROM_FILE.format(
                language=_LANGUAGE,
                endpoint_country=_ENDPOINT_COUNTRY,
                device=Device.IPHONE.value,
                uuid_1=str(uuid.uuid4()).upper(),
                uuid_2=str(uuid.uuid4()).upper(),
            ),
            content_type=_JSON_CONTENT_TYPE,
        ),
        Probe(
            url_name="ABOUT_TRACK",
            url=ShazamUrl.ABOUT_TRACK.format(
                language=_LANGUAGE,
                endpoint_country=_ENDPOINT_COUNTRY,
                track_id=_TRACK_ID,
            ),
            content_type=_JSON_CONTENT_TYPE,
        ),
        Probe(
            url_name="LOCATIONS",
            url=ShazamUrl.LOCATIONS,
            content_type=_JSON_CONTENT_TYPE,
        ),
        Probe(
            url_name="APPLE_IDS_TO_TRACK_KEYS",
            url=ShazamUrl.APPLE_IDS_TO_TRACK_KEYS.format(
                country=_ENDPOINT_COUNTRY,
                language=_LANGUAGE,
                apple_ids=_APPLE_ID,
            ),
            content_type=APPLE_TO_SHAZAM_CONTENT_TYPE,
        ),
        Probe(
            url_name="ITUNES_SEARCH",
            url=ShazamUrl.ITUNES_SEARCH
            + "?"
            + urlencode(
                {
                    "term": _SEARCH_TERM,
                    "entity": "song",
                    "limit": 1,
                    "country": _ENDPOINT_COUNTRY,
                },
            ),
            content_type=ITUNES_SEARCH_CONTENT_TYPE,
        ),
        _chart("TOP_WORLD_TRACKS", url=ShazamUrl.TOP_WORLD_TRACKS),
        _chart(
            "TOP_WORLD_GENRE_TRACKS",
            url=ShazamUrl.TOP_WORLD_GENRE_TRACKS.format(genre=_GENRE_SLUG),
        ),
        _chart(
            "TOP_COUNTRY_TRACKS",
            url=ShazamUrl.TOP_COUNTRY_TRACKS.format(country=_COUNTRY_SLUG),
        ),
        _chart(
            "TOP_COUNTRY_GENRE_TRACKS",
            url=ShazamUrl.TOP_COUNTRY_GENRE_TRACKS.format(
                country=_COUNTRY_SLUG,
                genre=_GENRE_SLUG,
            ),
        ),
        _chart(
            "TOP_CITY_TRACKS",
            url=ShazamUrl.TOP_CITY_TRACKS.format(
                country=_COUNTRY_SLUG,
                city=_CITY_SLUG,
            ),
        ),
        # An unknown slug is a clean empty `404`, which is the service working.
        _chart(
            "TOP_WORLD_GENRE_TRACKS",
            url=ShazamUrl.TOP_WORLD_GENRE_TRACKS.format(genre="no-such-genre"),
            expected=Verdict.BAD_INPUT,
        ),
        _chart(
            "TOP_COUNTRY_TRACKS",
            url=ShazamUrl.TOP_COUNTRY_TRACKS.format(country="no-such-country"),
            expected=Verdict.BAD_INPUT,
        ),
        _chart(
            "TOP_CITY_TRACKS",
            url=ShazamUrl.TOP_CITY_TRACKS.format(
                country=_COUNTRY_SLUG,
                city="no-such-city",
            ),
            expected=Verdict.BAD_INPUT,
        ),
    ]


def unprobed_url_names(checked: list[Probe]) -> set[str]:
    declared = {name for name in vars(ShazamUrl) if name.isupper()}
    return declared - {probe.url_name for probe in checked}


def classify(probe: Probe, *, answer: Answer) -> Verdict:
    # A retired path answers the website instead, often as `200 text/html`.
    if answer.content_type == "text/html":
        return Verdict.DEAD

    if probe.expected is Verdict.BAD_INPUT:
        is_clean_miss: bool = answer.status == HTTPStatus.NOT_FOUND and not answer.body
        return Verdict.BAD_INPUT if is_clean_miss else Verdict.UNEXPECTED

    if answer.status != HTTPStatus.OK or answer.content_type != probe.content_type:
        return Verdict.UNEXPECTED

    # `a2st` reports a bad request as `200 {"error":{"msg":"Could not fetch ids"}}`.
    if probe.content_type == APPLE_TO_SHAZAM_CONTENT_TYPE and "error" in json.loads(answer.body):
        return Verdict.UNEXPECTED

    return Verdict.LIVE


async def _recognition_payload() -> dict[str, Any]:
    signature = await Recognizer().recognize_path(value=str(_SAMPLE))

    return Converter.data_search(
        signature.timezone,
        signature.signature.uri,
        signature.signature.samples,
        signature.timestamp,
    )


async def _ask(session: aiohttp.ClientSession, *, probe: Probe) -> Answer:
    headers = Request(_LANGUAGE).headers()

    if probe.url_name == "SEARCH_FROM_FILE":
        request = session.post(
            probe.url,
            headers=headers,
            json=await _recognition_payload(),
        )
    else:
        request = session.get(
            probe.url,
            headers=headers,
            allow_redirects=False,
        )

    async with request as response:
        return Answer(
            status=response.status,
            content_type=response.content_type,
            body=await response.read(),
        )


def _report_line(probe: Probe, *, answer: Answer, verdict: Verdict) -> str:
    marker = "  " if verdict is probe.expected else "!!"
    shown = answer.body[:_SHOWN_BYTES]

    return (
        f"{marker} {verdict.value:<10} {answer.status} {answer.content_type:<25} "
        f"{len(answer.body):>9} B  {probe.url_name}  {probe.url}\n"
        f"{'':14}{shown!r}"
    )


async def main() -> int:
    all_probes = probes()
    unprobed = unprobed_url_names(all_probes)

    if unprobed:
        print(f"no probe for ShazamUrl.{', ShazamUrl.'.join(sorted(unprobed))}", file=sys.stderr)
        return 2

    surprises: int = 0

    # Serially: parallel requests to `www.` make live paths answer the website.
    async with aiohttp.ClientSession() as session:
        for probe in all_probes:
            answer = await _ask(session, probe=probe)
            verdict = classify(probe, answer=answer)
            surprises += verdict is not probe.expected

            print(
                _report_line(
                    probe,
                    answer=answer,
                    verdict=verdict,
                ),
            )

    print(f"\n{len(all_probes)} probed, {surprises} not as expected (marked !!)")
    return 1 if surprises else 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
