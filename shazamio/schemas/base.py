from typing import Generic
from typing import Optional
from typing import TypeVar

from pydantic import BaseModel
from pydantic.generics import GenericModel

T = TypeVar("T", bound=BaseModel)


class BaseHref(BaseModel):
    href: str


class BaseIdTypeHref(BaseHref):
    id: str
    type: str


class BaseIdTypeHrefAttributesModel(GenericModel, BaseIdTypeHref, Generic[T]):
    attributes: T


class BaseAttributesModel(GenericModel, BaseModel, Generic[T]):
    attributes: T


class BaseDataModel(GenericModel, BaseModel, Generic[T]):
    data: T


class BaseHrefNextData(GenericModel, BaseHref, Generic[T]):
    next: Optional[str] = None
    data: T


class BaseHrefData(GenericModel, BaseHref, Generic[T]):
    data: T
