from pydantic import BaseModel


class ChartTrack(BaseModel):
    """One row of a chart. Three columns is everything Shazam publishes."""

    rank: int
    artist: str
    title: str
