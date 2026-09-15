from typing import Any

from shazamio.schemas.models import ResponseTrack, TrackInfo


class Serialize:
    @classmethod
    def track(cls, data: dict[str, Any]) -> TrackInfo:
        return TrackInfo.model_validate(data)

    @classmethod
    def full_track(cls, data: dict[str, Any]) -> ResponseTrack:
        return ResponseTrack.model_validate(data)
