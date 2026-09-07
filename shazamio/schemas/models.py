from typing import Annotated
from typing import Any
from typing import List
from typing import Optional
from typing import Union
from urllib.parse import urlencode
from urllib.parse import urlparse
from urllib.parse import urlunparse
from uuid import UUID

from pydantic import AliasPath
from pydantic import BaseModel
from pydantic import Field


class ShareModel(BaseModel):
    subject: str
    text: str
    href: str
    image: str
    twitter: str
    html: str
    snapchat: str


class ActionModel(BaseModel):
    name: str
    type: str
    share: ShareModel
    uri: str


class SongMetaPages(BaseModel):
    image: str
    caption: str


class SongMetadata(BaseModel):
    title: str
    text: str


class SongSection(BaseModel):
    type: str
    meta_pages: List[SongMetaPages] = Field(validation_alias="metapages")
    tab_name: str = Field(validation_alias="tabname")
    metadata: List[SongMetadata]


class BaseIdTypeModel(BaseModel):
    type: str
    id: str


class TopTracksModel(BaseModel):
    url: str


class ArtistSection(BaseModel):
    type: str
    id: str
    name: str
    verified: bool
    actions: List[BaseIdTypeModel]
    tab_name: str = Field(validation_alias="tabname")
    top_tracks: TopTracksModel = Field(validation_alias="toptracks")


# Optional so a partial `beacondata` payload cannot fail the whole track load.
class BeaconDataLyricsSection(BaseModel):
    lyrics_id: Optional[str] = Field(default=None, validation_alias="lyricsid")
    provider_name: Optional[str] = Field(default=None, validation_alias="providername")
    common_track_id: Optional[str] = Field(default=None, validation_alias="commontrackid")


class LyricsSection(BaseModel):
    type: str
    text: List[str]
    footer: str
    tab_name: str = Field(validation_alias="tabname")
    beacon_data: Optional[BeaconDataLyricsSection] = Field(validation_alias="beacondata")


class VideoSection(BaseModel):
    tab_name: str = Field(validation_alias="tabname")
    youtube_url: str = Field(validation_alias="youtubeurl")
    type: str = "VIDEO"


class RelatedSection(BaseModel):
    type: str
    url: str
    tab_name: str = Field(validation_alias="tabname")


class DimensionsModel(BaseModel):
    width: int
    height: int


class YoutubeImageModel(BaseModel):
    dimensions: DimensionsModel
    url: str


class MatchModel(BaseModel):
    id: str
    offset: float
    time_skew: float = Field(validation_alias="timeskew")
    frequency_skew: float = Field(validation_alias="frequencyskew")
    channel: Optional[str] = None


class LocationModel(BaseModel):
    accuracy: float


class YoutubeData(BaseModel):
    caption: str
    image: YoutubeImageModel
    actions: List[ActionModel]
    uri: Optional[str] = None

    def model_post_init(self, context: Any, /) -> None:
        self.uri = self.__get_youtube_uri()

    def __get_youtube_uri(self) -> Optional[str]:
        if self.actions:
            for action in self.actions:
                if action.uri:
                    return action.uri
        return None


class TrackInfo(BaseModel):
    key: int
    title: str
    subtitle: str
    artist_id: Optional[str] = Field(default=None, validation_alias=AliasPath("artists", 0, "id"))
    shazam_url: Optional[str] = None
    # The old loader never populated this field, so no alias yet: it declared
    #  `init=False`, which `dataclass-factory` skips entirely.
    photo_url: Optional[str] = None
    spotify_uri_query: Optional[str] = None
    apple_music_url: Optional[str] = Field(
        default=None,
        validation_alias=AliasPath("hub", "options", 0, "actions", 0, "uri"),
    )
    ringtone: Optional[str] = Field(
        default=None,
        validation_alias=AliasPath("hub", "actions", 1, "uri"),
    )
    spotify_url: Optional[str] = Field(
        default=None,
        validation_alias=AliasPath("hub", "providers", 0, "actions", 0, "uri"),
    )
    spotify_uri: Optional[str] = Field(
        default=None,
        validation_alias=AliasPath("hub", "providers", 0, "actions", 1, "uri"),
    )
    youtube_link: Optional[str] = None
    # `left_to_right` keeps the old first-match parsing: an ARTIST section that
    #  also carries `url` and `tabname` still loads as `RelatedSection`.
    sections: Optional[
        List[
            Annotated[
                Union[
                    SongSection,
                    VideoSection,
                    LyricsSection,
                    RelatedSection,
                    ArtistSection,
                ],
                Field(union_mode="left_to_right"),
            ]
        ]
    ] = Field(default_factory=list)

    def model_post_init(self, context: Any, /) -> None:
        self.shazam_url = f"https://www.shazam.com/track/{self.artist_id}"
        self.apple_music_url = self.__apple_music_url()
        self.spotify_uri_query = self.__short_uri()
        self.youtube_link = self.__youtube_link()

    # `urlparse(None)` takes the bytes path, so a payload without `hub.options`
    #  ends with `apple_music_url = b""`.
    def __apple_music_url(self) -> Union[str, bytes]:
        url_parse_list = list(urlparse(self.apple_music_url))
        url_parse_list[4] = urlencode({}, doseq=True)
        url_deleted_query = urlunparse(url_parse_list)
        return url_deleted_query

    def __short_uri(self) -> Optional[str]:
        if self.spotify_uri:
            return self.spotify_uri.split("spotify:search:")[1]

        return None

    def __youtube_link(self) -> Optional[str]:
        for section in self.sections:
            if type(section) is VideoSection:
                return section.youtube_url

        return None


class ResponseTrack(BaseModel):
    tag_id: Optional[UUID] = Field(validation_alias="tagid")
    retry_ms: Optional[int] = Field(default=None, validation_alias="retryms")
    location: Optional[LocationModel] = None
    matches: List[MatchModel] = Field(default_factory=list)
    timestamp: Optional[int] = None
    timezone: Optional[str] = None
    track: Optional[TrackInfo] = None
