from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, Field

from shazamio.schemas.artist.views.top_music import PlayParams
from shazamio.schemas.attributes import AttributeName
from shazamio.schemas.base import (
    BaseAttributesModel,
    BaseHrefNext,
)
from shazamio.schemas.photos import ImageModel
from shazamio.schemas.urls import UrlDTO


class AttributesTopSong(BaseModel):
    has_time_synced_lyrics: bool = Field(..., alias="hasTimeSyncedLyrics")
    album_name: Optional[str] = Field(None, alias="albumName")
    genre_names: List = Field(..., alias="genreNames")
    track_number: int = Field(..., alias="trackNumber")
    release_date: str = Field(..., alias="releaseDate")
    duration_in_millis: int = Field(..., alias="durationInMillis")
    is_vocal_attenuation_allowed: bool = Field(..., alias="isVocalAttenuationAllowed")
    is_mastered_for_itunes: bool = Field(..., alias="isMasteredForItunes")
    isrc: str
    artwork: ImageModel
    composer_name: str = Field(..., alias="composerName")
    audio_locale: str = Field(..., alias="audioLocale")
    url: str
    play_params: PlayParams = Field(..., alias="playParams")
    disc_number: int = Field(..., alias="discNumber")
    has_lyrics: bool = Field(..., alias="hasLyrics")
    is_apple_digital_master: bool = Field(..., alias="isAppleDigitalMaster")
    audio_traits: List[str] = Field(..., alias="audioTraits")
    name: str
    previews: List[UrlDTO] = Field([])
    artist_name: str = Field(..., alias="artistName")
    content_rating: Optional[str] = Field(None, alias="contentRating")


class TopSong(BaseHrefNext):
    attributes: Optional[AttributeName] = None
    data: Optional[List[BaseAttributesModel[AttributesTopSong]]] = None
