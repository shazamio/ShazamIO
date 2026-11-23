from typing import Final

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
    "YOUTUBE_VIDEO_URL",
    "chart_path",
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
#
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
    # Each shape answers `200 text/csv`. `top-50/world/moscow`, and a
    #  genre the country does not offer, answer `404`:
    #  `curl -A 'Dalvik/2.1.0' https://www.shazam.com/services/charts/csv/top-50/russia/moscow/`
    if genre is not None and country is None:
        return f"genre/world/{genre}"

    if genre is not None:
        return f"genre/{country}/{genre}"

    if country is None:
        return "top-200/world"

    if city is None:
        return f"top-200/{country}"

    return f"top-50/{country}/{city}"
