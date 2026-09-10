from typing import Annotated, Any, Literal, TypeAlias
from urllib.parse import urlencode, urlparse, urlunparse
from uuid import UUID

from pydantic import AliasPath, BaseModel, Field


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
    type: Literal["SONG"]
    meta_pages: list[SongMetaPages] = Field(validation_alias="metapages")
    tab_name: str = Field(validation_alias="tabname")
    metadata: list[SongMetadata]


class BaseIdTypeModel(BaseModel):
    type: str
    id: str


class TopTracksModel(BaseModel):
    url: str


class ArtistSection(BaseModel):
    type: Literal["ARTIST"]
    id: str
    name: str
    verified: bool
    actions: list[BaseIdTypeModel]
    tab_name: str = Field(validation_alias="tabname")
    top_tracks: TopTracksModel = Field(validation_alias="toptracks")


# Optional so a partial `beacondata` payload cannot fail the whole track load.
class BeaconDataLyricsSection(BaseModel):
    lyrics_id: str | None = Field(default=None, validation_alias="lyricsid")
    provider_name: str | None = Field(default=None, validation_alias="providername")
    common_track_id: str | None = Field(default=None, validation_alias="commontrackid")


class LyricsSection(BaseModel):
    type: Literal["LYRICS"]
    text: list[str]
    footer: str
    tab_name: str = Field(validation_alias="tabname")
    beacon_data: BeaconDataLyricsSection | None = Field(validation_alias="beacondata")


class VideoSection(BaseModel):
    tab_name: str = Field(validation_alias="tabname")
    youtube_url: str = Field(validation_alias="youtubeurl")
    type: Literal["VIDEO"] = "VIDEO"


class RelatedSection(BaseModel):
    type: Literal["RELATED"]
    url: str
    tab_name: str = Field(validation_alias="tabname")


TrackSectionType: TypeAlias = Annotated[
    SongSection | VideoSection | LyricsSection | RelatedSection | ArtistSection,
    Field(discriminator="type"),
]


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
    channel: str | None = None


class LocationModel(BaseModel):
    accuracy: float


class YoutubeData(BaseModel):
    caption: str
    image: YoutubeImageModel
    actions: list[ActionModel]
    uri: str | None = None

    def model_post_init(self, _context: Any, /) -> None:
        self.uri = self.__get_youtube_uri()

    def __get_youtube_uri(self) -> str | None:
        if self.actions:
            for action in self.actions:
                if action.uri:
                    return action.uri
        return None


class TrackInfo(BaseModel):
    key: int
    title: str
    subtitle: str
    artist_id: str | None = Field(default=None, validation_alias=AliasPath("artists", 0, "id"))
    shazam_url: str | None = None
    photo_url: str | None = Field(
        default=None,
        validation_alias=AliasPath("images", "coverarthq"),
    )
    spotify_uri_query: str | None = None
    apple_music_url: str | None = Field(
        default=None,
        validation_alias=AliasPath("hub", "options", 0, "actions", 0, "uri"),
    )
    ringtone: str | None = Field(
        default=None,
        validation_alias=AliasPath("hub", "actions", 1, "uri"),
    )
    spotify_url: str | None = Field(
        default=None,
        validation_alias=AliasPath("hub", "providers", 0, "actions", 0, "uri"),
    )
    spotify_uri: str | None = Field(
        default=None,
        validation_alias=AliasPath("hub", "providers", 0, "actions", 1, "uri"),
    )
    youtube_link: str | None = None
    sections: list[TrackSectionType] | None = Field(default_factory=list)

    def model_post_init(self, _context: Any, /) -> None:
        self.shazam_url = f"https://www.shazam.com/track/{self.artist_id}"
        self.apple_music_url = self.__apple_music_url()
        self.spotify_uri_query = self.__short_uri()
        self.youtube_link = self.__youtube_link()

    # `urlparse(None)` takes the bytes path, so a payload without `hub.options`
    #  ends with `apple_music_url = b""`.
    def __apple_music_url(self) -> str | bytes:
        url_parse_list = list(urlparse(self.apple_music_url))
        url_parse_list[4] = urlencode({}, doseq=True)
        return urlunparse(url_parse_list)

    def __short_uri(self) -> str | None:
        if self.spotify_uri:
            return self.spotify_uri.split("spotify:search:")[1]

        return None

    def __youtube_link(self) -> str | None:
        for section in self.sections:
            if type(section) is VideoSection:
                return section.youtube_url

        return None


class ResponseTrack(BaseModel):
    tag_id: UUID | None = Field(validation_alias="tagid")
    retry_ms: int | None = Field(default=None, validation_alias="retryms")
    location: LocationModel | None = None
    matches: list[MatchModel] = Field(default_factory=list)
    timestamp: int | None = None
    timezone: str | None = None
    track: TrackInfo | None = None
