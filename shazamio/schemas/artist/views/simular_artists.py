from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, Field

from shazamio.schemas.attributes import AttributeName
from shazamio.schemas.base import BaseHrefNextData
from shazamio.schemas.base import BaseIdTypeHref
from shazamio.schemas.photos import ImageModel


class EditorialArtwork(BaseModel):
    centered_fullscreen_background: Optional[ImageModel] = Field(
        None, alias="centeredFullscreenBackground"
    )
    subscription_hero: Optional[ImageModel] = Field(None, alias="subscriptionHero")
    banner_uber: Optional[ImageModel] = Field(None, alias="bannerUber")


class Attributes(BaseModel):
    genre_names: List[str] = Field(..., alias="genreNames")
    editorial_artwork: EditorialArtwork = Field(..., alias="editorialArtwork")
    name: str
    artwork: ImageModel
    url: str
    origin: Optional[str] = None
    artist_bio: Optional[str] = Field(None, alias="artistBio")


class Relationships(BaseModel):
    albums: BaseHrefNextData[List[BaseIdTypeHref]]


class Datum(BaseIdTypeHref):
    attributes: Attributes
    relationships: Relationships


class SimularArtist(BaseModel):
    href: Optional[str] = None
    next: Optional[str] = None
    attributes: Optional[AttributeName] = None
    data: Optional[List[Datum]] = None
