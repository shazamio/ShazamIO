from typing import Any, Final

from pydantic import TypeAdapter

from shazamio.schemas.album import AlbumModel
from shazamio.schemas.artist.views.full_albums import FullAlbumsModel
from shazamio.schemas.artists import ArtistResponse, ArtistType
from shazamio.schemas.base import BaseDataModel
from shazamio.schemas.models import ResponseTrack, TrackInfo, YoutubeData
from shazamio.schemas.playlist.playlist import PlayList

ARTIST_ADAPTER: Final = TypeAdapter(ArtistType)


class Serialize:
    @classmethod
    def track(cls, data: dict[str, Any]) -> TrackInfo:
        return TrackInfo.model_validate(data)

    @classmethod
    def playlist(cls, data: dict[str, Any]) -> PlayList:
        return PlayList.model_validate(data)

    @classmethod
    def playlists(cls, data: dict[str, Any]) -> list[PlayList]:
        return [cls.playlist(pl) for pl in data.get("data", [])]

    @classmethod
    def youtube(cls, data: dict[str, Any]) -> YoutubeData:
        return YoutubeData.model_validate(data)

    @classmethod
    def artist_v2(cls, data: dict[str, Any]) -> ArtistResponse:
        return ArtistResponse.model_validate(data)

    @classmethod
    def artist_albums(cls, data: dict[str, Any]) -> FullAlbumsModel:
        return FullAlbumsModel.model_validate(data)

    @classmethod
    def artist(cls, data: dict[str, Any]) -> ArtistType:
        return ARTIST_ADAPTER.validate_python(data)

    @classmethod
    def full_track(cls, data: dict[str, Any]) -> ResponseTrack:
        return ResponseTrack.model_validate(data)

    @classmethod
    def album_info(cls, data: dict[str, Any]) -> BaseDataModel[list[AlbumModel]]:
        return BaseDataModel[list[AlbumModel]].model_validate(data)
