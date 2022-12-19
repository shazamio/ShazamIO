from typing import Union

from shazamio.factory_misc import FACTORY_ARTIST
from shazamio.factory_misc import FACTORY_TRACK
from shazamio.schemas.artists import ArtistInfo
from shazamio.schemas.artists import ArtistResponse
from shazamio.schemas.artists import ArtistV2
from shazamio.schemas.models import ResponseTrack
from shazamio.schemas.models import TrackInfo
from shazamio.schemas.models import YoutubeData


class Serialize:
    @classmethod
    def track(cls, data):
        return FACTORY_TRACK.load(data, TrackInfo)

    @classmethod
    def youtube(cls, data):
        return FACTORY_TRACK.load(data, YoutubeData)

    @classmethod
    def artist_v2(cls, data) -> ArtistResponse:
        return ArtistResponse.parse_obj(data)

    @classmethod
    def artist(cls, data):
        return FACTORY_ARTIST.load(data, Union[ArtistV2, ArtistInfo])

    @classmethod
    def full_track(cls, data):
        return FACTORY_TRACK.load(data, ResponseTrack)
