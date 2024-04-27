from dataclasses import dataclass
from dataclasses import field
from typing import List
from typing import Optional
from typing import Union

from pydantic import BaseModel
from pydantic import Field

from shazamio.schemas.base import BaseIdTypeHref
from shazamio.schemas.artist.views.full_albums import FullAlbumsModel
from shazamio.schemas.artist.views.last_release import LastReleaseModel
from shazamio.schemas.artist.views.simular_artists import SimularArtist
from shazamio.schemas.artist.views.top_music import TopMusicVideosView
from shazamio.schemas.artist.views.top_song import TopSong
from shazamio.schemas.attributes import ArtistAttribute
from shazamio.schemas.enums import ArtistExtend
from shazamio.schemas.enums import ArtistView
from shazamio.schemas.errors import ErrorModel


@dataclass
class ArtistInfo:
    name: str
    verified: Optional[bool]
    genres: Optional[List[str]] = field(default_factory=list)
    alias: Optional[str] = None
    genres_primary: Optional[str] = None
    avatar: Optional[Union[dict, str]] = None
    adam_id: Optional[int] = None
    url: Optional[str] = ""

    def __post_init__(self):
        self.avatar = self.__optional_avatar()

    def __optional_avatar(self) -> Optional[str]:
        if self.avatar is None:
            return None
        elif "default" in self.avatar:
            return self.avatar.get("default")
        else:
            return "".join(self.avatar)


@dataclass
class ArtistV2:
    artist: ArtistInfo


@dataclass
class ArtistQuery:
    views: List[ArtistView] = field(default_factory=list)
    extend: List[ArtistExtend] = field(default_factory=list)


@dataclass
class ArtistAvatar:
    width: int
    height: int
    url: str

    @classmethod
    def url_with_size(cls, height: int, width: int) -> str:
        return cls.url.format(w=width, h=height)


class AlbumRelationship(BaseModel):
    href: str
    next: Optional[str] = None
    data: List[BaseIdTypeHref]


class ArtistRelationships(BaseModel):
    albums: AlbumRelationship


class ArtistViews(BaseModel):
    top_music_videos: Optional[TopMusicVideosView] = Field(None, alias="top-music-videos")
    simular_artists: Optional[SimularArtist] = Field(None, alias="similar-artists")
    latest_release: Optional[LastReleaseModel] = Field(None, alias="latest-release")
    full_albums: Optional[FullAlbumsModel] = Field(None, alias="full-albums")
    top_songs: Optional[TopSong] = Field(None, alias="top-songs")


class ArtistV3(BaseModel):
    id: str
    type: str
    attributes: ArtistAttribute
    relationships: ArtistRelationships
    views: ArtistViews


class ArtistResponse(BaseModel):
    errors: List[ErrorModel] = []
    data: List[ArtistV3] = []
