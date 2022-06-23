from typing import Union

from shazamio.factory_misc import FACTORY_ARTIST
from shazamio.factory_misc import FACTORY_TRACK
from shazamio.models import ArtistInfo
from shazamio.models import ArtistV2
from shazamio.models import ResponseTrack
from shazamio.models import TrackInfo
from shazamio.models import YoutubeData


class Serialize:
    @classmethod
    def track(cls, data):
        return FACTORY_TRACK.load(data, TrackInfo)

    @classmethod
    def youtube(cls, data):
        return FACTORY_TRACK.load(data, YoutubeData)

    @classmethod
    def artist(cls, data):
        return FACTORY_ARTIST.load(data, Union[ArtistV2, ArtistInfo])

    @classmethod
    def full_track(cls, data):
        return FACTORY_TRACK.load(data, ResponseTrack)
