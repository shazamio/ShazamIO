from pydantic import BaseModel


class PlayParams(BaseModel):
    id: str
    kind: str
