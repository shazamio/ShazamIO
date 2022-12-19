from enum import Enum


class ArtistExtend(str, Enum):
    ARTIST_BIO = "artistBio"
    BORN_OF_FORMED = "bornOrFormed"
    EDITORIAL_ARTWORK = "editorialArtwork"
    ORIGIN = "origin"


class ArtistView(str, Enum):
    FULL_ALBUMS = "full-albums"
    FEATURED_ALBUMS = "featured-albums"
    LATEST_RELEASE = "latest-release"
    TOP_MUSIC_VIDEOS = "top-music-videos"
    SIMULAR_ARTISTS = "similar-artists"
    TOP_SONGS = "top-songs"
    PLAYLISTS = "playlists"
