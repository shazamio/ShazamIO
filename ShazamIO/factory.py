from dataclasses import dataclass, field
from typing import Optional, List

from dataclass_factory import Schema


@dataclass
class ArtistInfo:
    name: str
    alias: str
    verified: Optional[bool]
    genres: Optional[List[str]] = field(default_factory=list)
    genres_primary: Optional[str] = field(default_factory=str)
    avatar: Optional[str] = field(default_factory=str)
    url: Optional[str] = field(default_factory=str)

    def __str__(self):
        return (f'Name: {self.name}\n'
                f'Alias: {self.alias}\n'
                f'Verified: {self.verified}\n'
                f'Primary genre: {self.genres_primary}\n'
                f'All genres: {self.genres}\n'
                f'Url: {self.url}\n'
                f'Avatar: {self.avatar}')


artist_info_schema = Schema(
    name_mapping={
        "avatar": ("avatar", "default"),
        "genres": ("genres", "secondaries"),
        "genres_primary": ("genres", "primary"),
    }
)

