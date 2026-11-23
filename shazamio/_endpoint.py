import abc
from dataclasses import dataclass
from typing import ClassVar, Generic, TypeVar

from shazamio._enums import Device
from shazamio._service import JSON_CONTENT_TYPE
from shazamio._transport import Request

__all__ = [
    "Endpoint",
    "Settings",
]

# PEP 695 generics need Python 3.12, and the package supports 3.11.
_Answer = TypeVar("_Answer")


@dataclass(frozen=True, kw_only=True)
class Settings:
    """What every request of one `Shazam` shares."""

    __module__ = "shazamio"

    language: str
    country: str
    device: Device


class Endpoint(abc.ABC, Generic[_Answer]):
    """One call to a service: how to ask, and how to read the answer.

    `await shazam(endpoint)` sends `request()` through the middleware and the
    transport, checks that the answer is `200` and `content_type`, and returns
    `parse()` of its text.
    """

    __module__ = "shazamio"

    content_type: ClassVar[str] = JSON_CONTENT_TYPE

    @abc.abstractmethod
    def request(self, settings: Settings) -> Request:
        """The request to send for this call."""

    @abc.abstractmethod
    def parse(self, payload: str) -> _Answer:
        """The answer, from the text the service sent.

        :raises BadPayload: the text does not fit the answer
        """
