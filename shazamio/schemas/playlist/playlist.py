from pydantic import BaseModel, Field

from shazamio.schemas.base import BaseHrefData, BaseIdTypeHref
from shazamio.schemas.content_version import MetaContentVersion
from shazamio.schemas.photos import ImageModel
from shazamio.schemas.play_params import PlayParams
from shazamio.schemas.urls import UrlDTO


class PlayListRelationshipDTO(BaseModel):
    music_videos: BaseHrefData[list[BaseIdTypeHref]] = Field(
        default_factory=list,
        alias="music-videos",
    )
    artists: BaseHrefData[list[BaseIdTypeHref]] = Field(default_factory=list, alias="artists")


class PlayListAttributes(BaseModel):
    has_time_synced_lyrics: bool = Field(alias="hasTimeSyncedLyrics")
    album_name: str = Field(alias="albumName")
    genre_names: list[str] = Field(alias="genreNames")
    track_number: int = Field(alias="trackNumber")
    release_date: str | None = Field(default=None, alias="releaseDate")
    duration_in_millis: int | None = Field(default=None, alias="durationInMillis")
    is_vocal_attenuation_allowed: bool = Field(alias="isVocalAttenuationAllowed")
    is_mastered_for_itunes: bool = Field(alias="isMasteredForItunes")
    isrc: str
    artwork: ImageModel
    audio_locale: str = Field(alias="audioLocale")
    url: str
    play_params: PlayParams | None = Field(default=None, alias="playParams")
    disc_number: int = Field(alias="discNumber")
    has_credits: bool | None = Field(default=None, alias="hasCredits")
    is_apple_digital_master: bool = Field(alias="isAppleDigitalMaster")
    has_lyrics: bool = Field(alias="hasLyrics")
    audio_traits: list[str] = Field(alias="audioTraits")
    name: str
    previews: list[UrlDTO]
    content_rating: str | None = Field(default=None, alias="contentRating")
    artist_name: str = Field(alias="artistName")


class PlayList(BaseIdTypeHref):
    attributes: PlayListAttributes
    relationships: PlayListRelationshipDTO
    meta: MetaContentVersion
