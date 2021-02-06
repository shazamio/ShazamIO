from dataclass_factory import Factory
from ShazamIO.factory import ArtistInfo, artist_info_schema

factory_artist = Factory(schemas={ArtistInfo: artist_info_schema}, debug_path=True)

