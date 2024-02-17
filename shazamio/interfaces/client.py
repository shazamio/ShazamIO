import abc
from abc import ABC
from typing import Any


class HTTPClientInterface(ABC):
    @abc.abstractmethod
    async def request(
        self,
        method: str,
        url: str,
        *args,
        **kwargs,
    ) -> list[Any] | dict[str, Any]:
        raise NotImplementedError
