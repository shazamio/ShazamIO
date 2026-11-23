import abc
from collections.abc import Mapping
from dataclasses import dataclass, field
from http import HTTPMethod

__all__ = [
    "Request",
    "Response",
    "Transport",
]


@dataclass(frozen=True, kw_only=True)
class Request:
    """One HTTP request `Shazam` hands its transport."""

    method: HTTPMethod
    url: str
    headers: Mapping[str, str] = field(default_factory=dict)
    params: Mapping[str, str | int] = field(default_factory=dict)
    body: bytes | None = None


@dataclass(frozen=True, kw_only=True)
class Response:
    """What the service answered, whatever the status.

    `content_type` is the media type alone, without its parameters: `text/csv`.
    """

    status: int
    content_type: str
    text: str
    headers: Mapping[str, str] = field(default_factory=dict)


class Transport(abc.ABC):
    """Sends the requests of one `Shazam`.

    It only moves bytes: `Shazam` retries, checks the status and the content
    type and parses the answer, so every transport gets the same errors.
    """

    @abc.abstractmethod
    async def send(self, request: Request) -> Response:
        """Send `request` once and return the answer, whatever its status.

        :raises TransportError: no answer arrived, the transport's own error chained
        """

    @abc.abstractmethod
    async def close(self) -> None:
        """Release what the transport holds; `Shazam.close()` calls it."""
