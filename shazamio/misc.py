from enum import Enum
from random import choice
from shazamio.user_agent import USER_AGENTS


class ShazamUrl:
    SEARCH_FROM_FILE = (
        "https://amp.shazam.com/discovery/v5/{language}/{endpoint_country}/{device}/-/tag"
        "/{uuid_1}/{uuid_2}?sync=true&webv3=true&sampling=true"
        "&connected=&shazamapiversion=v3&sharehub=true&hubv5minorversion=v5.1&hidelb=true&video=v3"
    )
    ABOUT_TRACK = (
        "https://www.shazam.com/discovery/v5/{language}/{endpoint_country}/web/-/track"
        "/{track_id}?shazamapiversion=v3&video=v3 "
    )
    TOP_TRACKS_PLAYLIST = (
        "https://www.shazam.com/services/amapi/v1/catalog/{endpoint_country}"
        "/playlists/{playlist_id}/tracks?limit={limit}&offset={offset}&"
        "l={language}&relate[songs]=artists,music-videos"
    )
    LOCATIONS = "https://www.shazam.com/services/charts/locations"
    RELATED_SONGS = (
        "https://cdn.shazam.com/shazam/v3/{language}/{endpoint_country}/web/-/tracks"
        "/track-similarities-id-{track_id}?startFrom={offset}&pageSize={limit}&connected=&channel="
    )
    SEARCH_ARTIST = (
        "https://www.shazam.com/services/search/v4/{language}/{endpoint_country}/web"
        "/search?term={query}&limit={limit}&offset={offset}&types=artists"
    )
    SEARCH_MUSIC = (
        "https://www.shazam.com/services/search/v3/{language}/{endpoint_country}/web"
        "/search?query={query}&numResults={limit}&offset={offset}&types=songs"
    )
    LISTENING_COUNTER = "https://www.shazam.com/services/count/v2/web/track/{}"
    LISTENING_COUNTER_MANY = "https://www.shazam.com/services/count/v2/web/track"

    SEARCH_ARTIST_V2 = (
        "https://www.shazam.com/services/amapi/v1/catalog/{endpoint_country}/artists/{artist_id}"
    )
    ARTIST_ALBUMS = (
        "https://www.shazam.com/services/amapi/v1/catalog/{endpoint_country}"
        "/artists/{artist_id}/albums?limit={limit}&offset={offset}"
    )
    ARTIST_ALBUM_INFO = (
        "https://www.shazam.com/services/amapi/v1/catalog/{endpoint_country}/albums/{album_id}"
    )


class Request:
    TIME_ZONE = "Europe/Moscow"

    def __init__(self, language: str):
        self.language = language

    def headers(self):
        return {
            "X-Shazam-Platform": "IPHONE",
            "X-Shazam-AppVersion": "14.1.0",
            "Accept": "*/*",
            "Accept-Language": self.language,
            "Accept-Encoding": "gzip, deflate",
            "User-Agent": choice(USER_AGENTS),
        }


class Device(str, Enum):
    IPHONE = "iphone"
    ANDROID = "android"
    WEB = "web"

    @classmethod
    def random(cls) -> "Device":
        return choice([cls.IPHONE, cls.ANDROID, cls.WEB])
