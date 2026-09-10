from abc import ABC, abstractmethod
from typing import Any


class HTTPClientInterface(ABC):
    @abstractmethod
    async def request(
        self,
        method: str,
        url: str,
        *args: str,
        **kwargs: Any,
    ) -> list[Any] | dict[str, Any]:
        raise NotImplementedError
