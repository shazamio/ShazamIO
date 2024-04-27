from enum import IntEnum, Enum


class GenreMusic(Enum):
    POP = "pop"
    HIP_HOP_RAP = "hip-hop-rap"
    DANCE = "dance"
    ELECTRONIC = "electronic"
    RNB_SOUL = "randb-soul"
    ALTERNATIVE = "alternative"
    ROCK = "rock"
    LATIN = "latin"
    FILM_TV_STAGE = "film-tv-and-stage"
    COUNTRY = "country"
    AFRO_BEATS = "afrobeats"
    WORLDWIDE = "worldwide"
    REGGAE_DANCE_HALL = "reggae-dancehall"
    HOUSE = "house"
    K_POP = "k-pop"
    FRENCH_POP = "french-pop"
    SINGER_SONGWRITER = "singer-songwriter"
    REGIONAL_MEXICANO = "regional-mexicano"


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
