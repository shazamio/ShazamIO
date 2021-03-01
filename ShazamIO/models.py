from enum import IntEnum


class ShazamUrl:
    SEARCH_FROM_FILE = (
        'https://amp.shazam.com/discovery/v5/en/GB/iphone/-/tag/{}/{}?sync=true&webv3=true&sampling=true'
        '&connected=&shazamapiversion=v3&sharehub=true&hubv5minorversion=v5.1&hidelb=true&video=v3')
    TOP_TRACKS_WORLD = 'https://www.shazam.com/shazam/v3/en/GB/web/-/tracks/ip-global-chart?pageSize={}&startFrom={}'
    ARTIST_ABOUT = 'https://www.shazam.com/discovery/v3/en/GB/web/artist/{}?shazamapiversion=v3&video=v3'
    ARTIST_TOP_TRACKS = (
        'https://cdn.shazam.com/shazam/v3/en/GB/web/-/tracks/artisttoptracks_{}?startFrom={}'
        '&pageSize={}&connected=&channel=')
    ABOUT_TRACK = 'https://www.shazam.com/discovery/v5/en/GB/web/-/track/{}?shazamapiversion=v3&video=v3'
    TOP_TRACKS_COUNTRY = (
        'https://www.shazam.com/shazam/v3/en/GB/web/-/tracks/ip-country-chart-{}?pageSize={}&startFrom={}')
    TOP_TRACKS_CITY = (
        'https://www.shazam.com/shazam/v3/en/GB/web/-/tracks/ip-city-chart-{}?pageSize={}&startFrom={}')
    CITY_IDS = 'https://raw.githubusercontent.com/dotX12/dotX12/main/city.json'
    GENRE_WORLD = (
        "https://www.shazam.com/shazam/v3/en/GB/web/-/tracks/genre-global-chart-{}?pageSize={}&startFrom={}")
    GENRE_COUNTRY = (
        'https://www.shazam.com/shazam/v3/en/GB/web/-/tracks/genre-country-chart-{}-{}?pageSize={}&startFrom={}')
    RELATED_SONGS = (
        'https://cdn.shazam.com/shazam/v3/en/GB/web/-/tracks/track-similarities-id-{}'
        '?startFrom={}&pageSize={}&connected=&channel=')
    SEARCH_ARTIST = (
        'https://www.shazam.com/services/search/v3/en/GB/web/search?query={}'
        '&numResults={}&offset=0&types=artists')

    SEARCH_MUSIC = (
        'https://www.shazam.com/services/search/v3/en/GB/web/search?query={}'
        '&numResults={}&offset=0&types=songs')


class Request:
    LANG = 'ru'
    TIME_ZONE = 'Europe/Moscow'
    HEADERS = {
        "X-Shazam-Platform": "IPHONE",
        "X-Shazam-AppVersion": "14.1.0",
        "Accept": "*/*",
        "Accept-Language": LANG,
        "Accept-Encoding": "gzip, deflate",
        "User-Agent": "Shazam/3685 CFNetwork/1197 Darwin/20.0.0"
    }


class GenreMusic(IntEnum):
    POP = 1
    HIP_HOP_RAP = 2
    DANCE = 3
    ELECTRONIC = 4
    RNB_SOUL = 5
    ALTERNATIVE = 6
    ROCK = 7
    LATIN = 8
    FILM_TV_STAGE = 9
    COUNTRY = 10
    AFRO_BEATS = 11
    WORLDWIDE = 12
    REGGAE_DANCE_HALL = 13
    HOUSE = 14
    K_POP = 15
    FRENCH_POP = 16
    SINGER_SONGWRITER = 17
    REGIONAL_MEXICANO = 18


class SampleRate(IntEnum):
    # Enum keys are sample rates in Hz
    _8000 = 1
    _11025 = 2
    _16000 = 3
    _32000 = 4
    _44100 = 5
    _48000 = 6


class FrequencyBand(IntEnum):
    # Enum keys are frequency ranges in Hz
    hz_0_250 = -1  # Nothing above 250 Hz is actually stored
    hz_250_520 = 0
    hz_520_1450 = 1
    hz_1450_3500 = 2
    hz_3500_5500 = 3  # This one (3.5 KHz - 5.5 KHz) should not be used in legacy mode
