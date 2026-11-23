from random import choice
from typing import Any, Final

from shazamio_core import Signature

__all__ = [
    "APPLE_IDS_CONTENT_TYPE",
    "APPLE_IDS_URL",
    "CHART_CONTENT_TYPE",
    "CHART_URL",
    "ITUNES_SEARCH_CONTENT_TYPE",
    "ITUNES_SEARCH_MAX_LIMIT",
    "ITUNES_SEARCH_URL",
    "JSON_CONTENT_TYPE",
    "LOCATIONS_URL",
    "TAG_URL",
    "TRACK_URL",
    "USER_AGENTS",
    "YOUTUBE_VIDEO_URL",
    "chart_path",
    "headers",
    "tag_payload",
]

JSON_CONTENT_TYPE: Final[str] = "application/json"
TAG_URL: Final[str] = (
    "https://amp.shazam.com/discovery/v5/{language}/{country}/{device}/-/tag"
    "/{uuid_1}/{uuid_2}?sync=true&webv3=true&sampling=true"
    "&connected=&shazamapiversion=v3&sharehub=true&hubv5minorversion=v5.1&hidelb=true&video=v3"
)
# `discovery/v5` answers on `amp.` and `cdn.` only: `www.` returns the 1.7MB
#  single-page-app shell as `text/html` or answers `404`, either one a
#  `BadResponse`.
#  The device segment is `iphone`: the `web` profile omits `hub.providers`,
#  the Spotify and Deezer links, from every track, and `android` returns
#  `apple_music_url` as an `intent://` deep link no browser opens.
TRACK_URL: Final[str] = (
    "https://amp.shazam.com/discovery/v5/{language}/{country}/iphone/-/track"
    "/{track_id}?shazamapiversion=v3&video=v3"
)
# The URL the retired `VIDEO` track section used to carry, `GB` included.
#  `query` picks the video, and without it the service answers `400`. The
#  country picks among regional uploads, so `RU` can answer a different video.
#  `curl -s -w '%{http_code}' 'https://cdn.shazam.com/video/v3/-/GB/iphone/1/youtube/video'`
YOUTUBE_VIDEO_URL: Final[str] = (
    "https://cdn.shazam.com/video/v3/-/GB/iphone/{track_id}/youtube/video?q={query}"
)
LOCATIONS_URL: Final[str] = "https://www.shazam.com/services/charts/locations"
# `country` comes first and `locale` second: the other order answers
#  `200 {"error":{"msg":"Could not fetch ids"}}`, which reads like a dead
#  endpoint. The order is the one the website itself sends, from
#  `_next/static/chunks/1683-*.js`:
#  `fetch("/services/sd/s/a2st/".concat(t, "/").concat(n, "/").concat(e))`.
APPLE_IDS_URL: Final[str] = (
    "https://www.shazam.com/services/sd/s/a2st/{country}/{language}/{apple_ids}"
)
# The mapping is JSON served as `application/octet-stream`, so `response.json()`
#  raises `ContentTypeError` and the body is decoded by hand:
#  `curl -sI -A 'Dalvik/2.1.0 (Linux; U; Android 13; Pixel 7 Build/TQ3A)'
#  'https://www.shazam.com/services/sd/s/a2st/US/en-US/1125281672'`.
APPLE_IDS_CONTENT_TYPE: Final[str] = "application/octet-stream"
# Apple's index, not Shazam's: Shazam's own search answers `404 Not supported`,
#  `curl -A Dalvik/2.1.0 'https://www.shazam.com/services/search/v4/en-US/GB/web/search?term=adele'`.
ITUNES_SEARCH_URL: Final[str] = "https://itunes.apple.com/search"
# The search answers JSON as `text/javascript`, so `response.json()` raises
#  `ContentTypeError` and the body is decoded by hand:
#  `curl -sI 'https://itunes.apple.com/search?term=adele&entity=song&limit=1'`.
ITUNES_SEARCH_CONTENT_TYPE: Final[str] = "text/javascript"
# Apple serves `limit` from 1 to 200 (https://performance-partners.apple.com/search-api)
#  and answers `0` or a negative one with 20 songs, not with an error.
ITUNES_SEARCH_MAX_LIMIT: Final[int] = 200
# Charts are CSV only: on `cdn.`, the one host still routing the JSON ones,
#  `shazam/v3/.../tracks/ip-*-chart` answers `204` and `tracks/genre-*-chart-<id>`
#  a chart last updated in 2024, while the CSV is dated the current week.
#  Query parameters are ignored. `path` comes from `chart_path`.
CHART_URL: Final[str] = "https://www.shazam.com/services/charts/csv/{path}/"
CHART_CONTENT_TYPE: Final[str] = "text/csv"

# Only an app `User-Agent` reaches the API. `www.shazam.com` answers a browser
#  one with the website itself, which `Shazam` refuses by its content type;
#  a current Chrome string gets `405`. Every
#  agent below answers `200 text/csv` to
#  `curl -A '<agent>' https://www.shazam.com/services/charts/csv/top-200/world/`.
USER_AGENTS: Final[tuple[str, ...]] = (
    "Dalvik/2.1.0 (Linux; U; Android 5.0.2; VS980 4G Build/LRX22G)",
    "Dalvik/1.6.0 (Linux; U; Android 4.4.2; SM-T210 Build/KOT49H)",
    "Dalvik/2.1.0 (Linux; U; Android 5.1.1; SM-P905V Build/LMY47X)",
    "Dalvik/1.6.0 (Linux; U; Android 4.4.4; Vodafone Smart Tab 4G Build/KTU84P)",
    "Dalvik/1.6.0 (Linux; U; Android 4.4.4; SM-G360H Build/KTU84P)",
    "Dalvik/2.1.0 (Linux; U; Android 5.0.2; SM-S920L Build/LRX22G)",
    "Dalvik/2.1.0 (Linux; U; Android 5.0; Fire Pro Build/LRX21M)",
    "Dalvik/2.1.0 (Linux; U; Android 5.0; SM-N9005 Build/LRX21V)",
    "Dalvik/2.1.0 (Linux; U; Android 6.0.1; SM-G920F Build/MMB29K)",
    "Dalvik/1.6.0 (Linux; U; Android 4.4.2; SM-G7102 Build/KOT49H)",
    "Dalvik/2.1.0 (Linux; U; Android 5.0; SM-G900F Build/LRX21T)",
    "Dalvik/2.1.0 (Linux; U; Android 6.0.1; SM-G928F Build/MMB29K)",
    "Dalvik/2.1.0 (Linux; U; Android 5.1.1; SM-J500FN Build/LMY48B)",
    "Dalvik/2.1.0 (Linux; U; Android 5.1.1; Coolpad 3320A Build/LMY47V)",
    "Dalvik/1.6.0 (Linux; U; Android 4.4.4; SM-J110F Build/KTU84P)",
    "Dalvik/1.6.0 (Linux; U; Android 4.4.2; SAMSUNG-SGH-I747 Build/KOT49H)",
    "Dalvik/1.6.0 (Linux; U; Android 4.4.2; SAMSUNG-SM-T337A Build/KOT49H)",
    "Dalvik/1.6.0 (Linux; U; Android 4.3; SGH-T999 Build/JSS15J)",
    "Dalvik/2.1.0 (Linux; U; Android 6.0.1; D6603 Build/23.5.A.0.570)",
    "Dalvik/2.1.0 (Linux; U; Android 5.1.1; SM-J700H Build/LMY48B)",
    "Dalvik/1.6.0 (Linux; U; Android 4.4.2; HTC6600LVW Build/KOT49H)",
    "Dalvik/2.1.0 (Linux; U; Android 5.1.1; SM-N910G Build/LMY47X)",
    "Dalvik/2.1.0 (Linux; U; Android 5.1.1; SM-N910T Build/LMY47X)",
    "Dalvik/1.6.0 (Linux; U; Android 4.4.4; C6903 Build/14.4.A.0.157)",
    "Dalvik/1.6.0 (Linux; U; Android 4.2.2; GT-I9105P Build/JDQ39)",
    "Dalvik/1.6.0 (Linux; U; Android 4.4.2; GT-I9192 Build/KOT49H)",
    "Dalvik/2.1.0 (Linux; U; Android 5.1.1; SM-G531H Build/LMY48B)",
    "Dalvik/2.1.0 (Linux; U; Android 5.1.1; LGMS345 Build/LMY47V)",
    "Dalvik/2.1.0 (Linux; U; Android 5.0.2; HTC One Build/LRX22G)",
    "Dalvik/2.1.0 (Linux; U; Android 5.0.2; LG-D800 Build/LRX22G)",
    "Dalvik/1.6.0 (Linux; U; Android 4.4.4; SM-T113 Build/KTU84P)",
    "Dalvik/1.6.0 (Linux; U; Android 4.2.2; AndyWin Build/JDQ39E)",
    "Dalvik/2.1.0 (Linux; U; Android 5.0; Lenovo A7000-a Build/LRX21M)",
    "Dalvik/1.6.0 (Linux; U; Android 4.4.2; LGL16C Build/KOT49I.L16CV11a)",
    "Dalvik/1.6.0 (Linux; U; Android 4.4.2; GT-I9500 Build/KOT49H)",
    "Dalvik/2.1.0 (Linux; U; Android 5.0.2; SM-A700FD Build/LRX22G)",
    "Dalvik/1.6.0 (Linux; U; Android 4.4.2; SM-G130HN Build/KOT49H)",
    "Dalvik/1.6.0 (Linux; U; Android 4.4.2; SM-N9005 Build/KOT49H)",
    "Dalvik/1.6.0 (Linux; U; Android 4.1.2; LG-E975T Build/JZO54K)",
    "Dalvik/1.6.0 (Linux; U; Android 4.4.2; E1 Build/KOT49H)",
    "Dalvik/1.6.0 (Linux; U; Android 4.4.2; GT-N5100 Build/KOT49H)",
    "Dalvik/2.1.0 (Linux; U; Android 5.1.1; SM-A310F Build/LMY47X)",
    "Dalvik/2.1.0 (Linux; U; Android 5.1.1; SM-J105H Build/LMY47V)",
    "Dalvik/1.6.0 (Linux; U; Android 4.3; GT-I9305T Build/JSS15J)",
    "Dalvik/1.6.0 (Linux; U; Android 4.4.2; android Build/JDQ39)",
    "Dalvik/1.6.0 (Linux; U; Android 4.2.1; HS-U970 Build/JOP40D)",
    "Dalvik/1.6.0 (Linux; U; Android 4.4.4; SM-T561 Build/KTU84P)",
    "Dalvik/1.6.0 (Linux; U; Android 4.2.2; GT-P3110 Build/JDQ39)",
    "Dalvik/2.1.0 (Linux; U; Android 6.0.1; SM-G925T Build/MMB29K)",
    "Dalvik/1.6.0 (Linux; U; Android 4.4.2; HUAWEI Y221-U22 Build/HUAWEIY221-U22)",
    "Dalvik/2.1.0 (Linux; U; Android 5.1.1; SM-G530T1 Build/LMY47X)",
    "Dalvik/2.1.0 (Linux; U; Android 5.1.1; SM-G920I Build/LMY47X)",
    "Dalvik/2.1.0 (Linux; U; Android 5.1.1; Vodafone Smart ultra 6 Build/LMY47V)",
    "Dalvik/1.6.0 (Linux; U; Android 4.4.4; XT1080 Build/SU6-7.7)",
    "Dalvik/1.6.0 (Linux; U; Android 4.4.4; ASUS MeMO Pad 7 Build/KTU84P)",
    "Dalvik/1.6.0 (Linux; U; Android 4.4.2; SM-G800F Build/KOT49H)",
    "Dalvik/1.6.0 (Linux; U; Android 4.4.2; GT-N7100 Build/KOT49H)",
    "Dalvik/2.1.0 (Linux; U; Android 6.0.1; SM-G925I Build/MMB29K)",
    "Dalvik/2.1.0 (Linux; U; Android 6.0.1; A0001 Build/MMB29X)",
    "Dalvik/2.1.0 (Linux; U; Android 5.1; XT1045 Build/LPB23.13-61)",
    "Dalvik/2.1.0 (Linux; U; Android 5.1.1; LGMS330 Build/LMY47V)",
    "Dalvik/1.6.0 (Linux; U; Android 4.4.4; Z970 Build/KTU84P)",
    "Dalvik/2.1.0 (Linux; U; Android 5.0; SM-N900P Build/LRX21V)",
    "Dalvik/1.6.0 (Linux; U; Android 4.4.2; T1-701u Build/HuaweiMediaPad)",
    "Dalvik/2.1.0 (Linux; U; Android 5.1; HTCD100LVWPP Build/LMY47O)",
    "Dalvik/2.1.0 (Linux; U; Android 6.0.1; SM-G935R4 Build/MMB29M)",
    "Dalvik/2.1.0 (Linux; U; Android 6.0.1; SM-G930V Build/MMB29M)",
    "Dalvik/2.1.0 (Linux; U; Android 5.0.2; ZTE Blade Q Lux Build/LRX22G)",
    "Dalvik/1.6.0 (Linux; U; Android 4.4.4; GT-I9060I Build/KTU84P)",
    "Dalvik/2.1.0 (Linux; U; Android 6.0.1; LGUS992 Build/MMB29M)",
    "Dalvik/2.1.0 (Linux; U; Android 6.0.1; SM-G900P Build/MMB29M)",
    "Dalvik/1.6.0 (Linux; U; Android 4.1.2; SGH-T999L Build/JZO54K)",
    "Dalvik/2.1.0 (Linux; U; Android 5.1.1; SM-N910V Build/LMY47X)",
    "Dalvik/2.1.0 (Linux; U; Android 5.1.1; SM-P601 Build/LMY47X)",
    "Dalvik/1.6.0 (Linux; U; Android 4.2.2; GT-S7272 Build/JDQ39)",
    "Dalvik/1.6.0 (Linux; U; Android 4.3; SAMSUNG-SGH-I747 Build/JSS15J)",
    "Dalvik/2.1.0 (Linux; U; Android 6.0.1; SM-G930F Build/MMB29K)",
    "Dalvik/1.6.0 (Linux; U; Android 4.4.2; HTC_PO582 Build/KOT49H)",
    "Dalvik/2.1.0 (Linux; U; Android 6.0; HUAWEI MT7-TL10 Build/HuaweiMT7-TL10)",
    "Dalvik/2.1.0 (Linux; U; Android 6.0; LG-H811 Build/MRA58K)",
    "Dalvik/1.6.0 (Linux; U; Android 4.4.2; SM-N7505 Build/KOT49H)",
    "Dalvik/2.1.0 (Linux; U; Android 6.0; LG-H815 Build/MRA58K)",
    "Dalvik/1.6.0 (Linux; U; Android 4.4.2; LenovoA3300-HV Build/KOT49H)",
    "Dalvik/1.6.0 (Linux; U; Android 4.4.4; SM-G360G Build/KTU84P)",
    "Dalvik/1.6.0 (Linux; U; Android 4.4.4; GT-I9300I Build/KTU84P)",
    "Dalvik/2.1.0 (Linux; U; Android 6.0.1; SM-J700T Build/MMB29K)",
    "Dalvik/1.6.0 (Linux; U; Android 4.2.2; SM-T217S Build/JDQ39)",
    "Dalvik/1.6.0 (Linux; U; Android 4.4.4; SAMSUNG-SM-N900A Build/KTU84P)",
)


def headers(language: str) -> dict[str, str]:
    return {
        "X-Shazam-Platform": "IPHONE",
        "X-Shazam-AppVersion": "14.1.0",
        "Accept": "*/*",
        "Accept-Language": language,
        "Accept-Encoding": "gzip, deflate",
        # Picking a user agent is not cryptographic.
        "User-Agent": choice(USER_AGENTS),  # noqa: S311
    }


def tag_payload(signature: Signature) -> dict[str, Any]:
    return {
        "timezone": signature.timezone,
        "signature": {
            "uri": signature.signature.uri,
            "samplems": signature.signature.samples,
        },
        "timestamp": signature.timestamp,
        "context": {},
        "geolocation": {},
    }


def chart_path(
    *,
    country: str | None = None,
    city: str | None = None,
    genre: str | None = None,
) -> str:
    """The `CHART_URL` path of a chart, from the slugs `LOCATIONS_URL` lists.

    :param country: country `urlName`, `None` for worldwide
    :param city: city `urlName`, only with a country and without a genre
    :param genre: `GenreMusic` value
    """
    if genre is not None:
        return f"genre/{country or 'world'}/{genre}"

    if country is None:
        return "top-200/world"

    if city is None:
        return f"top-200/{country}"

    return f"top-50/{country}/{city}"
