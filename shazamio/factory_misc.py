from dataclass_factory import Factory

from shazamio.factory import TrackInfo, FactorySchemas, ArtistInfo

FACTORY_TRACK = Factory(schemas={TrackInfo: FactorySchemas.FACTORY_TRACK_SCHEMA}, debug_path=True)
FACTORY_ARTIST = Factory(schemas={ArtistInfo: FactorySchemas.FACTORY_ARTIST_SCHEMA}, debug_path=True)


def serialize_track(data):
    return FACTORY_TRACK.load(data, TrackInfo)


def serialize_artist(data):
    return FACTORY_ARTIST.load(data, ArtistInfo)
