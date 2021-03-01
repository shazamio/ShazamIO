from enum import IntEnum


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