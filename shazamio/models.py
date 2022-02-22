from dataclasses import dataclass
from dataclasses import field
from typing import List
from typing import Optional
from typing import Union
from urllib.parse import urlencode
from urllib.parse import urlparse
from urllib.parse import urlunparse
from uuid import UUID

from dataclass_factory import Factory


@dataclass
class ArtistInfo(Factory):
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
class ShareModel:
    subject: str
    text: str
    href: str
    image: str
    twitter: str
    html: str
    snapchat: str


@dataclass
class ActionModel:
    name: str
    type: str
    share: ShareModel
    uri: str


@dataclass
class SongMetaPages:
    image: str
    caption: str


@dataclass
class SongMetadata:
    title: str
    text: str


@dataclass
class SongSection:
    type: str
    meta_pages: List[SongMetaPages]
    tab_name: str
    metadata: List[SongMetadata]


@dataclass
class VideoSection:
    type: str
    tab_name: str
    youtube_url: str


@dataclass
class RelatedSection:
    type: str
    url: str
    tab_name: str


@dataclass
class DimensionsModel:
    width: int
    height: int


@dataclass
class YoutubeImageModel:
    dimensions: DimensionsModel
    url: str


@dataclass
class MatchModel:
    id: str
    offset: float
    channel: str
    timeskew: float
    frequencyskew: float


@dataclass
class LocationModel:
    accuracy: float


@dataclass
class YoutubeData:
    caption: str
    image: YoutubeImageModel
    actions: List[ActionModel]
    uri: Optional[str] = None

    def __post_init__(self):
        self.uri = self.__get_youtube_uri()

    def __get_youtube_uri(self):
        if self.actions:
            for action in self.actions:
                if action.uri:
                    return action.uri


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
    youtube_link: Optional[str] = None
    _sections: Optional[List[Union[SongSection, VideoSection, RelatedSection]]] = field(
        default_factory=list
    )

    def __post_init__(self):
        self.shazam_url = f'https://www.shazam.com/track/{self.artist_id}'
        self.apple_music_url = self.__apple_music_url()
        self.spotify_uri_query = self.__short_uri()
        self.youtube_link = self.__youtube_link()

    def __apple_music_url(self):
        url_parse_list = list(urlparse(self.apple_music_url))
        url_parse_list[4] = urlencode({}, doseq=True)
        url_deleted_query = urlunparse(url_parse_list)
        return url_deleted_query

    def __short_uri(self):
        if self.spotify_uri:
            return self.spotify_uri.split('spotify:search:')[1]

    def __youtube_link(self):
        for i in self._sections:
            if type(i) is VideoSection:
                return i.youtube_url


@dataclass
class ResponseTrack:
    tag_id: Optional[UUID]
    retryms: Optional[int] = field(default=None)
    location: Optional[LocationModel] = field(default=None)
    matches: List[MatchModel] = field(default_factory=list)
    timestamp: Optional[int] = field(default=None)
    timezone: Optional[str] = field(default=None)
    track: Optional[TrackInfo] = field(default=None)
