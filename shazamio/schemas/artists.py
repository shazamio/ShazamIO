from dataclasses import dataclass, field
from typing import Annotated, Any, TypeAlias

from pydantic import AliasPath, BaseModel, Field

from shazamio.schemas.artist.views.full_albums import FullAlbumsModel
from shazamio.schemas.artist.views.last_release import LastReleaseModel
from shazamio.schemas.artist.views.simular_artists import SimularArtist
from shazamio.schemas.artist.views.top_music import TopMusicVideosView
from shazamio.schemas.artist.views.top_song import TopSong
from shazamio.schemas.attributes import ArtistAttribute
from shazamio.schemas.base import BaseIdTypeHref
from shazamio.schemas.enums import ArtistExtend, ArtistView
from shazamio.schemas.errors import ErrorModel


class ArtistInfo(BaseModel):
    name: str
    verified: bool | None
    genres: list[str] | None = Field(
        default_factory=list,
        validation_alias=AliasPath("genres", "secondaries"),
    )
    alias: str | None = None
    genres_primary: str | None = Field(
        default=None,
        validation_alias=AliasPath("genres", "primary"),
    )
    avatar: dict[str, str] | str | None = None
    adam_id: int | None = Field(default=None, validation_alias="adamid")
    url: str | None = Field(default="", validation_alias="weburl")

    def model_post_init(self, _context: Any, /) -> None:
        self.avatar = self.__optional_avatar()

    def __optional_avatar(self) -> str | None:
        if self.avatar is None:
            return None
        if "default" in self.avatar:
            return self.avatar.get("default")
        return "".join(self.avatar)


class ArtistV2(BaseModel):
    artist: ArtistInfo


# `left_to_right` keeps the old parser's first-match union semantics; the two
#  shapes share no field a discriminator could read.
ArtistType: TypeAlias = Annotated[
    ArtistV2 | ArtistInfo,
    Field(union_mode="left_to_right"),
]


@dataclass
class ArtistQuery:
    views: list[ArtistView] = field(default_factory=list)
    extend: list[ArtistExtend] = field(default_factory=list)


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
    next: str | None = None
    data: list[BaseIdTypeHref]


class ArtistRelationships(BaseModel):
    albums: AlbumRelationship


class ArtistViews(BaseModel):
    top_music_videos: TopMusicVideosView | None = Field(default=None, alias="top-music-videos")
    simular_artists: SimularArtist | None = Field(default=None, alias="similar-artists")
    latest_release: LastReleaseModel | None = Field(default=None, alias="latest-release")
    full_albums: FullAlbumsModel | None = Field(default=None, alias="full-albums")
    top_songs: TopSong | None = Field(default=None, alias="top-songs")


class ArtistV3(BaseModel):
    id: str
    type: str
    attributes: ArtistAttribute
    relationships: ArtistRelationships
    views: ArtistViews


class ArtistResponse(BaseModel):
    errors: list[ErrorModel] = []
    data: list[ArtistV3] = []
