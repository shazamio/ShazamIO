from __future__ import annotations

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from shazamio.schemas.play_params import PlayParams
from shazamio.schemas.attributes import AttributeName
from shazamio.schemas.base import BaseAttributesModel
from shazamio.schemas.photos import ImageModel


class Preview(BaseModel):
    url: str
    hls_url: str = Field(..., alias="hlsUrl")
    artwork: ImageModel


class Attributes(BaseModel):
    genre_names: List[str] = Field(..., alias="genreNames")
    release_date: str = Field(..., alias="releaseDate")
    duration_in_millis: int = Field(..., alias="durationInMillis")
    isrc: str
    artwork: ImageModel
    play_params: PlayParams = Field(..., alias="playParams")
    url: str
    has4_k: bool = Field(..., alias="has4K")
    editorial_artwork: Dict[str, Any] = Field(..., alias="editorialArtwork")
    has_hdr: bool = Field(..., alias="hasHDR")
    name: str
    previews: List[Preview]
    artist_name: str = Field(..., alias="artistName")
    content_rating: Optional[str] = Field(None, alias="contentRating")
    album_name: Optional[str] = Field(None, alias="albumName")
    track_number: Optional[int] = Field(None, alias="trackNumber")


class TopMusicVideosView(BaseModel):
    href: Optional[str] = None
    attributes: Optional[AttributeName] = None
    data: Optional[List[BaseAttributesModel[Attributes]]] = None
