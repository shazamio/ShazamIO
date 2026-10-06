from enum import Enum


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
    # `regional-mexicano` was renamed to `m%C3%BAsica-mexicana` and is the one
    #  genre `services/charts/locations` lists that has no chart: every chart
    #  path built from either spelling answers `404` with an empty body.
