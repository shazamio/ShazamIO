"""The calls `Shazam` makes, one class each: `await shazam(endpoint)` runs any of them."""

import json
import uuid
from collections.abc import Sequence
from dataclasses import dataclass
from http import HTTPMethod
from typing import ClassVar, TypeVar

from pydantic import BaseModel, Field, ValidationError
from shazamio_core import Signature

from shazamio import _service as service
from shazamio._endpoint import Endpoint, Settings
from shazamio._exceptions import BadPayload
from shazamio._parsers import parse_apple_ids, parse_chart, parse_itunes_track_ids
from shazamio._transport import Request
from shazamio.models import ChartTrack, ResponseTrack, TrackInfo, YoutubeData

__all__ = [
    "ItunesSearch",
    "RecognizeSignature",
    "TrackAbout",
    "TrackKeysFromAppleIds",
    "YoutubeVideo",
]

# PEP 695 generics need Python 3.12, and the package supports 3.11.
_Model = TypeVar("_Model", bound=BaseModel)


class _City(BaseModel):
    name: str
    url_name: str = Field(alias="urlName")


class _Country(BaseModel):
    code: str = Field(alias="id")
    url_name: str = Field(alias="urlName")
    cities: list[_City]


class _Locations(BaseModel):
    countries: list[_Country]


def _parse_model(
    model: type[_Model],
    *,
    payload: str,
) -> _Model:
    try:
        return model.model_validate_json(payload)
    except ValidationError as er:
        msg = f"Shazam answer is not a `{model.__name__}`: {payload[:200]}"
        raise BadPayload(msg) from er


@dataclass(frozen=True, kw_only=True)
class TrackAbout(Endpoint[TrackInfo]):
    """A track by its Shazam key, such as `549952578`."""

    track_id: int

    def request(self, settings: Settings) -> Request:
        return Request(
            method=HTTPMethod.GET,
            url=service.TRACK_URL.format(
                language=settings.language,
                country=settings.country,
                track_id=self.track_id,
            ),
            headers=service.headers(settings.language),
        )

    def parse(self, payload: str) -> TrackInfo:
        return _parse_model(TrackInfo, payload=payload)


@dataclass(frozen=True, kw_only=True)
class TrackKeysFromAppleIds(Endpoint[dict[str, str]]):
    """Apple Music track ids mapped to Shazam track keys, as `Shazam.track_keys_from_apple_ids`."""

    content_type: ClassVar[str] = service.APPLE_IDS_CONTENT_TYPE

    apple_ids: Sequence[int | str]

    def __post_init__(self) -> None:
        # An empty sequence asks for `.../{language}/`, which answers
        #  `404 text/html Not supported` and reads as a dead endpoint.
        if not self.apple_ids:
            msg: str = "No Apple ids given"
            raise ValueError(msg)

    def request(self, settings: Settings) -> Request:
        return Request(
            method=HTTPMethod.GET,
            url=service.APPLE_IDS_URL.format(
                country=settings.country,
                language=settings.language,
                apple_ids=",".join(str(apple_id) for apple_id in self.apple_ids),
            ),
            headers=service.headers(settings.language),
        )

    def parse(self, payload: str) -> dict[str, str]:
        return parse_apple_ids(payload)


@dataclass(frozen=True, kw_only=True)
class ItunesSearch(Endpoint[list[int]]):
    """The Apple track ids of the songs Apple's iTunes search finds, in its order."""

    content_type: ClassVar[str] = service.ITUNES_SEARCH_CONTENT_TYPE

    query: str
    limit: int = 5

    def __post_init__(self) -> None:
        if not 1 <= self.limit <= service.ITUNES_SEARCH_MAX_LIMIT:
            msg = f"`limit` must be from 1 to {service.ITUNES_SEARCH_MAX_LIMIT}, got {self.limit}"
            raise ValueError(msg)

    def request(self, settings: Settings) -> Request:
        return Request(
            method=HTTPMethod.GET,
            url=service.ITUNES_SEARCH_URL,
            # Apple's search is no Shazam endpoint, so it gets none of its headers.
            params={
                "term": self.query,
                "entity": "song",
                "limit": self.limit,
                "country": settings.country,
            },
        )

    def parse(self, payload: str) -> list[int]:
        return parse_itunes_track_ids(payload)


@dataclass(frozen=True, kw_only=True)
class YoutubeVideo(Endpoint[YoutubeData]):
    """The YouTube video Shazam shows for a track, from its `youtube_link`."""

    link: str

    def request(self, settings: Settings) -> Request:
        return Request(
            method=HTTPMethod.GET,
            url=self.link,
            headers=service.headers(settings.language),
        )

    def parse(self, payload: str) -> YoutubeData:
        return _parse_model(YoutubeData, payload=payload)


@dataclass(frozen=True, kw_only=True)
class RecognizeSignature(Endpoint[ResponseTrack]):
    """The Shazam answer for a signature `shazamio_core` computed."""

    signature: Signature

    def request(self, settings: Settings) -> Request:
        return Request(
            method=HTTPMethod.POST,
            url=service.TAG_URL.format(
                language=settings.language,
                country=settings.country,
                device=settings.device.value,
                # SongRec sends random v4 ids:
                #  https://github.com/marin-m/SongRec/blob/b94ee61d51f40e8b3051da8f5c6a9e9c437b3633/src/core/fingerprinting/communication.rs#L89-L90
                uuid_1=str(uuid.uuid4()).upper(),
                uuid_2=str(uuid.uuid4()).upper(),
            ),
            headers={
                **service.headers(settings.language),
                "Content-Type": service.JSON_CONTENT_TYPE,
            },
            body=json.dumps(service.tag_payload(self.signature)).encode(),
        )

    def parse(self, payload: str) -> ResponseTrack:
        return _parse_model(ResponseTrack, payload=payload)


# The chart endpoints stay private: their slugs come from the locations answer,
#  which `Shazam.top_tracks` reads for the caller.
@dataclass(frozen=True, kw_only=True)
class _ChartLocations(Endpoint[_Locations]):
    def request(self, settings: Settings) -> Request:
        return Request(
            method=HTTPMethod.GET,
            url=service.LOCATIONS_URL,
            headers=service.headers(settings.language),
        )

    def parse(self, payload: str) -> _Locations:
        return _parse_model(_Locations, payload=payload)


@dataclass(frozen=True, kw_only=True)
class _Chart(Endpoint[list[ChartTrack]]):
    content_type: ClassVar[str] = service.CHART_CONTENT_TYPE

    path: str

    def request(self, settings: Settings) -> Request:
        return Request(
            method=HTTPMethod.GET,
            url=service.CHART_URL.format(path=self.path),
            headers=service.headers(settings.language),
        )

    def parse(self, payload: str) -> list[ChartTrack]:
        return parse_chart(payload)
