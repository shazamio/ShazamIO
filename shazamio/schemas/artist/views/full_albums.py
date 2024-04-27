from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, Field

from shazamio.schemas.play_params import PlayParams
from shazamio.schemas.attributes import AttributeName
from shazamio.schemas.base import BaseIdTypeHrefAttributesModel
from shazamio.schemas.photos import ImageModel


class EditorialArtwork(BaseModel):
    subscription_hero: Optional[ImageModel] = Field(None, alias="subscriptionHero")
    store_flow_case: Optional[ImageModel] = Field(None, alias="storeFlowcase")


class EditorialNotes(BaseModel):
    standard: Optional[str] = None
    short: Optional[str] = None


class AttributesFullAlbums(BaseModel):
    copyright: str
    genre_names: List[str] = Field(..., alias="genreNames")
    release_date: str = Field(..., alias="releaseDate")
    is_mastered_for_itunes: bool = Field(..., alias="isMasteredForItunes")
    upc: str
    artwork: ImageModel
    play_params: PlayParams = Field(..., alias="playParams")
    url: str
    record_label: str = Field(..., alias="recordLabel")
    track_count: int = Field(..., alias="trackCount")
    is_compilation: bool = Field(..., alias="isCompilation")
    is_prerelease: bool = Field(..., alias="isPrerelease")
    audio_traits: List[str] = Field(..., alias="audioTraits")
    editorial_artwork: Optional[EditorialArtwork] = Field(None, alias="editorialArtwork")
    is_single: bool = Field(..., alias="isSingle")
    name: str
    artist_name: str = Field(..., alias="artistName")
    content_rating: Optional[str] = Field(None, alias="contentRating")
    is_complete: bool = Field(..., alias="isComplete")
    editorial_notes: Optional[EditorialNotes] = Field(None, alias="editorialNotes")


class FullAlbumsModel(BaseModel):
    href: Optional[str] = None
    attributes: Optional[AttributeName] = None
    data: List[BaseIdTypeHrefAttributesModel[AttributesFullAlbums]] = Field([])


class SmallAlbumsModel(BaseModel):
    href: Optional[str] = None
    attributes: Optional[AttributeName] = None
    data: List[BaseIdTypeHrefAttributesModel[AttributesFullAlbums]] = Field([])
