from pydantic import BaseModel, Field


class AttributeName(BaseModel):
    title: str


class ArtistAttribute(BaseModel):
    genre_names: list[str] = Field(default_factory=list, alias="genreNames")
    name: str
    url: str
    artist_bio: str | None = Field(default=None, alias="artistBio")
