from dataclasses import dataclass
from dataclasses import field
from typing import List
from typing import Optional
from typing import Union
from urllib.parse import urlencode
from urllib.parse import urlparse
from urllib.parse import urlunparse
from uuid import UUID


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
class BaseIdTypeModel:
    type: str
    id: str


@dataclass
class TopTracksModel:
    url: str


@dataclass
class ArtistSection:
    type: str
    id: str
    name: str
    verified: bool
    actions: List[BaseIdTypeModel]
    tab_name: str
    top_tracks: TopTracksModel


class BeaconDataLyricsSection:
    lyrics_id: str
    provider_name: str
    common_track_id: str


@dataclass
class LyricsSection:
    type: str
    text: List[str]
    footer: str
    tab_name: str
    beacon_data: Optional[BeaconDataLyricsSection]


@dataclass
class VideoSection:
    tab_name: str
    youtube_url: str
    type: str = "VIDEO"


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
    time_skew: float
    frequency_skew: float
    channel: Optional[str] = field(default=None)


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
class TrackInfo:
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
    sections: Optional[
        List[
            Union[
                SongSection,
                VideoSection,
                LyricsSection,
                RelatedSection,
                ArtistSection,
            ]
        ]
    ] = field(default_factory=list)

    def __post_init__(self):
        self.shazam_url = f"https://www.shazam.com/track/{self.artist_id}"
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
            return self.spotify_uri.split("spotify:search:")[1]

    def __youtube_link(self):
        for i in self.sections:
            if type(i) is VideoSection:
                return i.youtube_url


@dataclass
class ResponseTrack:
    tag_id: Optional[UUID]
    retry_ms: Optional[int] = field(default=None)
    location: Optional[LocationModel] = field(default=None)
    matches: List[MatchModel] = field(default_factory=list)
    timestamp: Optional[int] = field(default=None)
    timezone: Optional[str] = field(default=None)
    track: Optional[TrackInfo] = field(default=None)
