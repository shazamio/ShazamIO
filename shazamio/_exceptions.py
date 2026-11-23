from functools import partial
from typing import Any, Self

__all__ = [
    "BadPayload",
    "BadResponse",
    "NotFound",
    "RateLimited",
    "ShazamError",
]


class ShazamError(Exception):
    """Base of every error the library raises on purpose."""

    __module__ = "shazamio"


class BadResponse(ShazamError):
    """The service answered with something other than the API answer."""

    __module__ = "shazamio"

    def __init__(
        self,
        message: str,
        *,
        url: str,
        status: int,
    ) -> None:
        super().__init__(message)
        self._url = url
        self._status = status

    # `pickle` rebuilds an exception from `args`, the message alone, so without
    #  this `pickle.loads` raised `TypeError: BadResponse.__init__() missing 2
    #  required keyword-only arguments: 'url' and 'status'`. The `__dict__`
    #  carries what `add_note` attached, typed `Any` as `object.__dict__` is.
    def __reduce__(self) -> tuple[partial[Self], tuple[str], dict[str, Any]]:
        rebuild = partial(
            type(self),
            url=self._url,
            status=self._status,
        )

        return rebuild, (str(self),), self.__dict__

    @property
    def url(self) -> str:
        return self._url

    @property
    def status(self) -> int:
        return self._status


class RateLimited(BadResponse):
    """The service throttled the request."""

    __module__ = "shazamio"


class BadPayload(ShazamError):
    """The answer arrived and fits no model."""

    __module__ = "shazamio"


class NotFound(ShazamError, LookupError):
    """A country, city or Apple id the service does not know."""

    __module__ = "shazamio"
