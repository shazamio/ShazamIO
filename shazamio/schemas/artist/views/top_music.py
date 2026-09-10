from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

from shazamio.schemas.attributes import AttributeName
from shazamio.schemas.base import BaseAttributesModel
from shazamio.schemas.photos import ImageModel
from shazamio.schemas.play_params import PlayParams


class Preview(BaseModel):
    url: str
    hls_url: str = Field(alias="hlsUrl")
    artwork: ImageModel


class Attributes(BaseModel):
    genre_names: list[str] = Field(alias="genreNames")
    release_date: str = Field(alias="releaseDate")
    duration_in_millis: int = Field(alias="durationInMillis")
    isrc: str
    artwork: ImageModel
    play_params: PlayParams = Field(alias="playParams")
    url: str
    has4_k: bool = Field(alias="has4K")
    editorial_artwork: dict[str, Any] = Field(alias="editorialArtwork")
    has_hdr: bool = Field(alias="hasHDR")
    name: str
    previews: list[Preview]
    artist_name: str = Field(alias="artistName")
    content_rating: str | None = Field(default=None, alias="contentRating")
    album_name: str | None = Field(default=None, alias="albumName")
    track_number: int | None = Field(default=None, alias="trackNumber")


class TopMusicVideosView(BaseModel):
    href: str | None = None
    attributes: AttributeName | None = None
    data: list[BaseAttributesModel[Attributes]] | None = None
