from __future__ import annotations

from pydantic import BaseModel, Field

from shazamio.schemas.attributes import AttributeName
from shazamio.schemas.base import BaseIdTypeHrefAttributesModel
from shazamio.schemas.photos import ImageModel
from shazamio.schemas.play_params import PlayParams


class EditorialArtwork(BaseModel):
    subscription_hero: ImageModel | None = Field(default=None, alias="subscriptionHero")
    store_flow_case: ImageModel | None = Field(default=None, alias="storeFlowcase")


class EditorialNotes(BaseModel):
    standard: str | None = None
    short: str | None = None


class AttributesFullAlbums(BaseModel):
    copyright: str
    genre_names: list[str] = Field(alias="genreNames")
    release_date: str = Field(alias="releaseDate")
    is_mastered_for_itunes: bool = Field(alias="isMasteredForItunes")
    upc: str
    artwork: ImageModel
    play_params: PlayParams = Field(alias="playParams")
    url: str
    record_label: str = Field(alias="recordLabel")
    track_count: int = Field(alias="trackCount")
    is_compilation: bool = Field(alias="isCompilation")
    is_prerelease: bool = Field(alias="isPrerelease")
    audio_traits: list[str] = Field(alias="audioTraits")
    editorial_artwork: EditorialArtwork | None = Field(default=None, alias="editorialArtwork")
    is_single: bool = Field(alias="isSingle")
    name: str
    artist_name: str = Field(alias="artistName")
    content_rating: str | None = Field(default=None, alias="contentRating")
    is_complete: bool = Field(alias="isComplete")
    editorial_notes: EditorialNotes | None = Field(default=None, alias="editorialNotes")


class FullAlbumsModel(BaseModel):
    href: str | None = None
    attributes: AttributeName | None = None
    data: list[BaseIdTypeHrefAttributesModel[AttributesFullAlbums]] = Field(default_factory=list)


class SmallAlbumsModel(BaseModel):
    href: str | None = None
    attributes: AttributeName | None = None
    data: list[BaseIdTypeHrefAttributesModel[AttributesFullAlbums]] = Field(default_factory=list)
