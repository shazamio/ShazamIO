from dataclass_factory import Factory

from shazamio.factory import FactorySchemas
from shazamio.models import ArtistInfo
from shazamio.models import SongSection, VideoSection, RelatedSection
from shazamio.models import TrackInfo
from shazamio.models import YoutubeData
from shazamio.models import ResponseTrack

FACTORY_TRACK = Factory(schemas={
    TrackInfo: FactorySchemas.FACTORY_TRACK_SCHEMA,
    SongSection: FactorySchemas.FACTORY_SONG_SECTION_SCHEMA,
    VideoSection: FactorySchemas.FACTORY_VIDEO_SECTION_SCHEMA,
    RelatedSection: FactorySchemas.FACTORY_RELATED_SECTION_SCHEMA,
    YoutubeData: FactorySchemas.FACTORY_YOUTUBE_TRACK_SCHEMA,
    ResponseTrack: FactorySchemas.FACTORY_RESPONSE_TRACK_SCHEMA,
}, debug_path=True)

FACTORY_ARTIST = Factory(
    schemas={ArtistInfo: FactorySchemas.FACTORY_ARTIST_SCHEMA},
    debug_path=True
)
