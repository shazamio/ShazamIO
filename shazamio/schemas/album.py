from typing import Optional, List

from pydantic import BaseModel, Field

from shazamio.schemas.artist.views.full_albums import AttributesFullAlbums
from shazamio.schemas.artist.views.top_song import AttributesTopSong
from shazamio.schemas.base import BaseHref, BaseIdTypeHref


class TrackInfoDTO(AttributesTopSong):
    has_credits: Optional[bool] = Field(None, alias="hasCredits")


class TrackInfoWithHref(BaseIdTypeHref):
    id: str
    type: str
    href: str
    attributes: TrackInfoDTO


class TrackModel(BaseHref):
    href: str
    data: List[TrackInfoWithHref] = Field([])


class ArtistModel(BaseHref):
    data: List[BaseIdTypeHref] = Field([])


class AlbumRelationships(BaseModel):
    artists: ArtistModel
    tracks: TrackModel


class AlbumModel(BaseModel):
    id: str
    type: str
    href: str
    attributes: AttributesFullAlbums
    relationships: AlbumRelationships
