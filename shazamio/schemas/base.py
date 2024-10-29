from typing import Generic
from typing import Optional
from typing import TypeVar

from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)


class BaseHref(BaseModel):
    href: str


class BaseIdTypeHref(BaseHref):
    id: str
    type: str


class BaseHrefNext(BaseHref):
    next: Optional[str] = None


class BaseIdTypeHrefAttributesModel(BaseIdTypeHref, Generic[T]):
    attributes: T


class BaseAttributesModel(BaseModel, Generic[T]):
    attributes: T


class BaseDataModel(BaseModel, Generic[T]):
    data: T


class BaseHrefNextData(BaseHrefNext, Generic[T]):
    data: T


class BaseHrefData(BaseHref, Generic[T]):
    data: T
