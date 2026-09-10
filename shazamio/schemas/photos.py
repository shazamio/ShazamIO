from pydantic import BaseModel, Field


class ImageModel(BaseModel):
    width: int
    url: str
    height: int
    text_color3: str | None = Field(default=None, alias="textColor3")
    text_color2: str | None = Field(default=None, alias="textColor2")
    text_color4: str | None = Field(default=None, alias="textColor4")
    text_color1: str | None = Field(default=None, alias="textColor1")
    bg_color: str | None = Field(default=None, alias="bgColor")
    has_p3: bool = Field(alias="hasP3")
