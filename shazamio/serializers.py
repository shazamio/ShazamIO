from typing import Union, List

from shazamio.factory_misc import FACTORY_ARTIST, FACTORY_TRACK
from shazamio.schemas.album import AlbumModel
from shazamio.schemas.artist.views.full_albums import FullAlbumsModel
from shazamio.schemas.artists import (
    ArtistInfo,
    ArtistResponse,
    ArtistV2,
)
from shazamio.schemas.base import BaseDataModel
from shazamio.schemas.models import (
    ResponseTrack,
    TrackInfo,
    YoutubeData,
)
from shazamio.schemas.playlist.playlist import PlayList


class Serialize:
    @classmethod
    def track(cls, data):
        return FACTORY_TRACK.load(data, TrackInfo)

    @classmethod
    def playlist(cls, data) -> PlayList:
        return PlayList.parse_obj(data)

    @classmethod
    def playlists(cls, data) -> List[PlayList]:
        return [cls.playlist(pl) for pl in data.get("data", [])]

    @classmethod
    def youtube(cls, data):
        return FACTORY_TRACK.load(data, YoutubeData)

    @classmethod
    def artist_v2(cls, data) -> ArtistResponse:
        return ArtistResponse.parse_obj(data)

    @classmethod
    def artist_albums(cls, data) -> FullAlbumsModel:
        return FullAlbumsModel.parse_obj(data)

    @classmethod
    def artist(cls, data):
        return FACTORY_ARTIST.load(data, Union[ArtistV2, ArtistInfo])

    @classmethod
    def full_track(cls, data):
        return FACTORY_TRACK.load(data, ResponseTrack)

    @classmethod
    def album_info(cls, data) -> BaseDataModel[List[AlbumModel]]:
        return BaseDataModel[List[AlbumModel]].parse_obj(data)
