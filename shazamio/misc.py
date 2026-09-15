from enum import Enum
from random import choice
from typing import Final

from shazamio.user_agent import USER_AGENTS


class ShazamUrl:
    SEARCH_FROM_FILE: Final[str] = (
        "https://amp.shazam.com/discovery/v5/{language}/{endpoint_country}/{device}/-/tag"
        "/{uuid_1}/{uuid_2}?sync=true&webv3=true&sampling=true"
        "&connected=&shazamapiversion=v3&sharehub=true&hubv5minorversion=v5.1&hidelb=true&video=v3"
    )
    # `discovery/v5` answers on `amp.` and `cdn.` only. On `www.` it returns the
    #  1.7MB single-page-app shell as `text/html`, which surfaces as
    #  `FailedDecodeJson` and reads like a parsing bug.
    #  The device segment is `iphone` because the `web` profile omits
    #  `hub.providers`, the Spotify and Deezer links, from every track it
    #  answers with, while `android` returns `apple_music_url` as an
    #  `intent://` deep link no browser opens.
    ABOUT_TRACK: Final[str] = (
        "https://amp.shazam.com/discovery/v5/{language}/{endpoint_country}/iphone/-/track"
        "/{track_id}?shazamapiversion=v3&video=v3"
    )
    RELATED_SONGS: Final[str] = (
        "https://cdn.shazam.com/shazam/v3/{language}/{endpoint_country}/iphone/-/tracks"
        "/track-similarities-id-{track_id}?startFrom={offset}&pageSize={limit}&connected=&channel="
    )
    LOCATIONS: Final[str] = "https://www.shazam.com/services/charts/locations"
    # Charts are CSV and only CSV: the JSON chart resources are dead or
    #  frozen. On `cdn.` (the only host still routing them)
    #  `shazam/v3/.../tracks/ip-*-chart` answers `204`, and
    #  `tracks/genre-*-chart-<id>` a chart last updated in 2024, while the CSV
    #  below is dated the current week. Columns are `Rank,Artist,Title` and
    #  query parameters are ignored, so paging is a client-side slice.
    TOP_WORLD_TRACKS: Final[str] = "https://www.shazam.com/services/charts/csv/top-200/world/"
    TOP_WORLD_GENRE_TRACKS: Final[str] = (
        "https://www.shazam.com/services/charts/csv/genre/world/{genre}/"
    )
    TOP_COUNTRY_TRACKS: Final[str] = "https://www.shazam.com/services/charts/csv/top-200/{country}/"
    TOP_COUNTRY_GENRE_TRACKS: Final[str] = (
        "https://www.shazam.com/services/charts/csv/genre/{country}/{genre}/"
    )
    TOP_CITY_TRACKS: Final[str] = (
        "https://www.shazam.com/services/charts/csv/top-50/{country}/{city}/"
    )


class Request:
    TIME_ZONE = "Europe/Moscow"

    def __init__(self, language: str) -> None:
        self.language = language

    def headers(self) -> dict[str, str]:
        return {
            "X-Shazam-Platform": "IPHONE",
            "X-Shazam-AppVersion": "14.1.0",
            "Accept": "*/*",
            "Accept-Language": self.language,
            "Accept-Encoding": "gzip, deflate",
            # Picking a user agent is not cryptographic.
            "User-Agent": choice(USER_AGENTS),  # noqa: S311
        }


class Device(str, Enum):
    IPHONE = "iphone"
    ANDROID = "android"
    WEB = "web"
