from enum import StrEnum
from random import choice
from typing import Final

from shazamio.user_agent import USER_AGENTS


class ShazamUrl:
    SEARCH_FROM_FILE: Final[str] = (
        "https://amp.shazam.com/discovery/v5/{language}/{endpoint_country}/{device}/-/tag"
        "/{uuid_1}/{uuid_2}?sync=true&webv3=true&sampling=true"
        "&connected=&shazamapiversion=v3&sharehub=true&hubv5minorversion=v5.1&hidelb=true&video=v3"
    )
    # `discovery/v5` answers on `amp.` and `cdn.` only: `www.` returns the 1.7MB
    #  single-page-app shell as `text/html`, which surfaces as `FailedDecodeJson`
    #  and reads like a parsing bug.
    #  The device segment is `iphone`: the `web` profile omits `hub.providers`,
    #  the Spotify and Deezer links, from every track, and `android` returns
    #  `apple_music_url` as an `intent://` deep link no browser opens.
    ABOUT_TRACK: Final[str] = (
        "https://amp.shazam.com/discovery/v5/{language}/{endpoint_country}/iphone/-/track"
        "/{track_id}?shazamapiversion=v3&video=v3"
    )
    # The URL the retired `VIDEO` track section used to carry, `GB` included.
    #  `query` alone picks the video, any `track_id` answers the same one, and
    #  without it the service answers `400`. The country picks among regional
    #  uploads, so `RU` can answer a different video.
    #  `curl -s -w '%{http_code}' 'https://cdn.shazam.com/video/v3/-/GB/iphone/1/youtube/video'`
    YOUTUBE_VIDEO: Final[str] = (
        "https://cdn.shazam.com/video/v3/-/GB/iphone/{track_id}/youtube/video?q={query}"
    )
    LOCATIONS: Final[str] = "https://www.shazam.com/services/charts/locations"
    # `country` comes first and `locale` second: the other order answers
    #  `200 {"error":{"msg":"Could not fetch ids"}}`, which reads like a dead
    #  endpoint. The order is the one the website itself sends, from
    #  `_next/static/chunks/1683-*.js`:
    #  `fetch("/services/sd/s/a2st/".concat(t, "/").concat(n, "/").concat(e))`.
    APPLE_IDS_TO_TRACK_KEYS: Final[str] = (
        "https://www.shazam.com/services/sd/s/a2st/{country}/{language}/{apple_ids}"
    )
    # Apple's index, not Shazam's: Shazam's own search answers `404 Not supported`,
    #  `curl -A Dalvik/2.1.0 'https://www.shazam.com/services/search/v4/en-US/GB/web/search?term=adele'`.
    ITUNES_SEARCH: Final[str] = "https://itunes.apple.com/search"
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


class Device(StrEnum):
    IPHONE = "iphone"
    ANDROID = "android"
    WEB = "web"
