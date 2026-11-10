from typing import Any

from shazamio.schemas.models import ResponseTrack, TrackInfo, YoutubeData

__all__ = ["Serialize"]


# The `Shazam` methods return these models, so these only parse stored payloads;
#  a model passed in comes back unchanged, which keeps pre-model callers working.
#  https://github.com/pydantic/pydantic/blob/aa540acc29960fb394312cf97d888c99f9686814/pydantic/config.py#L491-L492
class Serialize:
    @classmethod
    def track(cls, data: dict[str, Any] | TrackInfo) -> TrackInfo:
        return TrackInfo.model_validate(data)

    @classmethod
    def full_track(cls, data: dict[str, Any] | ResponseTrack) -> ResponseTrack:
        return ResponseTrack.model_validate(data)

    @classmethod
    def youtube(cls, data: dict[str, Any] | YoutubeData) -> YoutubeData:
        return YoutubeData.model_validate(data)
