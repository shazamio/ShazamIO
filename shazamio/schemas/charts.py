from pydantic import BaseModel

__all__ = ["ChartTrack"]


class ChartTrack(BaseModel):
    """One row of a chart. Three columns is everything Shazam publishes."""

    rank: int
    artist: str
    title: str
