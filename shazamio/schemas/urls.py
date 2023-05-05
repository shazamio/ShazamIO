from pydantic import BaseModel


class UrlDTO(BaseModel):
    url: str
