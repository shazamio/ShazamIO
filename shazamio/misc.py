from random import choice
from shazamio.user_agent import USER_AGENTS


class ShazamUrl:
    SEARCH_FROM_FILE = (
        "https://amp.shazam.com/discovery/v5/en/GB/iphone/-/tag/{}/{"
        "}?sync=true&webv3=true&sampling=true "
        "&connected=&shazamapiversion=v3&sharehub=true&hubv5minorversion=v5.1&hidelb=true&video=v3"
    )
    TOP_TRACKS_WORLD = (
        "https://www.shazam.com/shazam/v3/en/GB/web/-/tracks/ip-global-chart"
        "?pageSize={}&startFrom={}"
    )
    ARTIST_ABOUT = (
        "https://www.shazam.com/discovery/v3/en/GB/web/artist/{" "}?shazamapiversion=v3&video=v3 "
    )
    ARTIST_TOP_TRACKS = (
        "https://cdn.shazam.com/shazam/v3/en/GB/web/-/tracks/artisttoptracks_{}?startFrom={}"
        "&pageSize={}&connected=&channel="
    )
    ABOUT_TRACK = (
        "https://www.shazam.com/discovery/v5/en/GB/web/-/track/{" "}?shazamapiversion=v3&video=v3 "
    )
    TOP_TRACKS_COUNTRY = (
        "https://www.shazam.com/shazam/v3/en/GB/web/-/tracks/ip-country-chart-{}?pageSize={"
        "}&startFrom={}"
    )
    TOP_TRACKS_CITY = (
        "https://www.shazam.com/shazam/v3/en/GB/web/-/tracks/ip-city-chart-{}?pageSize={"
        "}&startFrom={}"
    )
    CITY_IDS = "https://raw.githubusercontent.com/dotX12/dotX12/main/city.json"
    GENRE_WORLD = (
        "https://www.shazam.com/shazam/v3/en/GB/web/-/tracks/genre-global-chart-{}?pageSize={"
        "}&startFrom={}"
    )
    GENRE_COUNTRY = (
        "https://www.shazam.com/shazam/v3/en/GB/web/-/tracks/genre-country-chart-{}-{}?pageSize={"
        "}&startFrom={}"
    )
    RELATED_SONGS = (
        "https://cdn.shazam.com/shazam/v3/en/GB/web/-/tracks/track-similarities-id-{}"
        "?startFrom={}&pageSize={}&connected=&channel="
    )
    SEARCH_ARTIST = (
        "https://www.shazam.com/services/search/v4/en-US/RU/web/search?term={}"
        "&offset=0&limit={}&types=artists"
    )
    SEARCH_MUSIC = (
        "https://www.shazam.com/services/search/v3/en/GB/web/search?query={}"
        "&numResults={}&offset=0&types=songs"
    )
    LISTENING_COUNTER = "https://www.shazam.com/services/count/v2/web/track/{}"

    SEARCH_ARTIST_V2 = "https://www.shazam.com/services/amapi/v1/catalog/{language}/artists/{}"


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
