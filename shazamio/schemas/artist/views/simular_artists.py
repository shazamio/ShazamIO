from __future__ import annotations

from pydantic import BaseModel, Field

from shazamio.schemas.attributes import AttributeName
from shazamio.schemas.base import BaseHrefNextData, BaseIdTypeHref
from shazamio.schemas.photos import ImageModel


class EditorialArtwork(BaseModel):
    centered_fullscreen_background: ImageModel | None = Field(
        default=None,
        alias="centeredFullscreenBackground",
    )
    subscription_hero: ImageModel | None = Field(default=None, alias="subscriptionHero")
    banner_uber: ImageModel | None = Field(default=None, alias="bannerUber")


class Attributes(BaseModel):
    genre_names: list[str] = Field(alias="genreNames")
    editorial_artwork: EditorialArtwork = Field(alias="editorialArtwork")
    name: str
    artwork: ImageModel
    url: str
    origin: str | None = None
    artist_bio: str | None = Field(default=None, alias="artistBio")


class Relationships(BaseModel):
    albums: BaseHrefNextData[list[BaseIdTypeHref]]


class Datum(BaseIdTypeHref):
    attributes: Attributes
    relationships: Relationships


class SimularArtist(BaseModel):
    href: str | None = None
    next: str | None = None
    attributes: AttributeName | None = None
    data: list[Datum] | None = None
