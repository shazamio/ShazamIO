from typing import Any, Dict, Final, List

from pydantic import TypeAdapter

from shazamio.schemas.base import BaseDataModel
from shazamio.schemas.artist.views.full_albums import FullAlbumsModel
from shazamio.schemas.artists import ArtistResponse
from shazamio.schemas.artists import ArtistType
from shazamio.schemas.models import ResponseTrack
from shazamio.schemas.models import TrackInfo
from shazamio.schemas.models import YoutubeData
from shazamio.schemas.album import AlbumModel
from shazamio.schemas.playlist.playlist import PlayList

ARTIST_ADAPTER: Final = TypeAdapter(ArtistType)


class Serialize:
    @classmethod
    def track(cls, data: Dict[str, Any]) -> TrackInfo:
        return TrackInfo.model_validate(data)

    @classmethod
    def playlist(cls, data: Dict[str, Any]) -> PlayList:
        return PlayList.model_validate(data)

    @classmethod
    def playlists(cls, data: Dict[str, Any]) -> List[PlayList]:
        return [cls.playlist(pl) for pl in data.get("data", [])]

    @classmethod
    def youtube(cls, data: Dict[str, Any]) -> YoutubeData:
        return YoutubeData.model_validate(data)

    @classmethod
    def artist_v2(cls, data: Dict[str, Any]) -> ArtistResponse:
        return ArtistResponse.model_validate(data)

    @classmethod
    def artist_albums(cls, data: Dict[str, Any]) -> FullAlbumsModel:
        return FullAlbumsModel.model_validate(data)

    @classmethod
    def artist(cls, data: Dict[str, Any]) -> ArtistType:
        return ARTIST_ADAPTER.validate_python(data)

    @classmethod
    def full_track(cls, data: Dict[str, Any]) -> ResponseTrack:
        return ResponseTrack.model_validate(data)

    @classmethod
    def album_info(cls, data: Dict[str, Any]) -> BaseDataModel[List[AlbumModel]]:
        return BaseDataModel[List[AlbumModel]].model_validate(data)
