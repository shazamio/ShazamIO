from __future__ import annotations

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from shazamio.schemas.play_params import PlayParams
from shazamio.schemas.attributes import AttributeName
from shazamio.schemas.base import BaseAttributesModel
from shazamio.schemas.photos import ImageModel


class AttributeLastRelease(BaseModel):
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
    editorial_artwork: Dict[str, Any] = Field(..., alias="editorialArtwork")
    is_single: bool = Field(..., alias="isSingle")
    name: str
    artist_name: str = Field(..., alias="artistName")
    content_rating: Optional[str] = Field(None, alias="contentRating")
    is_complete: bool = Field(..., alias="isComplete")


class LastReleaseModel(BaseModel):
    href: Optional[str] = None
    attributes: Optional[AttributeName] = None
    data: Optional[List[BaseAttributesModel[AttributeLastRelease]]] = None
