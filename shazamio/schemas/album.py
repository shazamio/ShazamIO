from pydantic import BaseModel, Field

from shazamio.schemas.artist.views.full_albums import AttributesFullAlbums
from shazamio.schemas.artist.views.top_song import AttributesTopSong
from shazamio.schemas.base import BaseHref, BaseIdTypeHref


class TrackInfoDTO(AttributesTopSong):
    has_credits: bool | None = Field(default=None, alias="hasCredits")


class TrackInfoWithHref(BaseIdTypeHref):
    attributes: TrackInfoDTO


class TrackModel(BaseHref):
    href: str
    data: list[TrackInfoWithHref] = Field(default_factory=list)


class ArtistModel(BaseHref):
    data: list[BaseIdTypeHref] = Field(default_factory=list)


class AlbumRelationships(BaseModel):
    artists: ArtistModel
    tracks: TrackModel


class AlbumModel(BaseIdTypeHref):
    attributes: AttributesFullAlbums
    relationships: AlbumRelationships
