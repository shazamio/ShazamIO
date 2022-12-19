from typing import List
from typing import Optional

from pydantic import BaseModel
from pydantic import Field


class AttributeName(BaseModel):
    title: str


class ArtistAttribute(BaseModel):
    genre_names: List[str] = Field([], alias="genreNames")
    name: str
    url: str
    artist_bio: Optional[str] = Field(None, alias="artistBio")
