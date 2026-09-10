from abc import ABC, abstractmethod
from typing import Any


class HTTPClientInterface(ABC):
    @abstractmethod
    async def request(
        self,
        method: str,
        url: str,
        *args,
        **kwargs,
    ) -> list[Any] | dict[str, Any]:
        raise NotImplementedError
