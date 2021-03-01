from dataclasses import field
from typing import Optional, List, Union
from urllib.parse import urlparse, urlencode, urlunparse
from dataclass_factory import Factory, Schema
from dataclasses import dataclass


@dataclass
class ArtistInfo:
    name: str
    alias: str
    verified: Optional[bool]
    genres: Optional[List[str]] = field(default_factory=list)
    genres_primary: Optional[str] = None
    avatar: Optional[Union[dict, str]] = None
    url: Optional[str] = ''

    def __post_init__(self):
        self.avatar = self.__optional_avatar()

    def __optional_avatar(self):
        if self.avatar is None:
            return None
        elif 'default' in self.avatar:
            return self.avatar.get('default')
        else:
            return ''.join(self.avatar)


@dataclass
class TrackInfo(Factory):
    key: int
    title: str
    subtitle: str
    artist_id: Optional[str] = field(default=None)
    shazam_url: str = None
    photo_url: Optional[str] = field(init=False, default=None)
    spotify_uri_query: Optional[str] = None
    apple_music_url: Optional[str] = None
    ringtone: Optional[str] = None
    spotify_url: Optional[str] = field(default=None)
    spotify_uri: Optional[str] = field(default=None)

    def __post_init__(self):
        self.shazam_url = f'https://www.shazam.com/track/{self.artist_id}'
        self.apple_music_url = self.__apple_music_url()
        self.spotify_uri_query = self.__short_uri()

    def __apple_music_url(self):
        url_parse_list = list(urlparse(self.apple_music_url))
        url_parse_list[4] = urlencode({}, doseq=True)
        url_deleted_query = urlunparse(url_parse_list)
        return url_deleted_query

    def __short_uri(self):
        if self.spotify_uri:
            return self.spotify_uri.split('spotify:search:')[1]


class FactoryTrack:
    def __init__(self, data):
        self.__data = data
        self.__schema = Schema(
            name_mapping={
                "photo_url": ("images", "coverarthq"),
                "ringtone": ("hub", "actions", 1, "uri"),
                "artist_id": ("artists", 0, "id"),
                "apple_music_url": ("hub", "options", 0, "actions", 0, "uri"),
                "spotify_url": ("hub", "providers", 0, "actions", 0, "uri"),
                "spotify_uri": ("hub", "providers", 0, "actions", 1, "uri")
            }, skip_internal=True)

    def serializer(self):
        factory = Factory(schemas={TrackInfo: self.__schema}, debug_path=True)
        return factory.load(self.__data, TrackInfo)


class FactoryArtist:
    def __init__(self, data):
        self.__data = data
        self.__schema = Schema(
            name_mapping={
                "avatar": "avatar",
                "genres": ("genres", "secondaries"),
                "genres_primary": ("genres", "primary"),
            })

    def serializer(self):
        factory = Factory(schemas={ArtistInfo: self.__schema}, debug_path=True)
        return factory.load(self.__data, ArtistInfo)
