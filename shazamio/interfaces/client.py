from abc import ABC, abstractmethod
from typing import Any


class HTTPClientInterface(ABC):
    @abstractmethod
    async def request(
        self,
        method: str,
        url: str,
        **kwargs: Any,
    ) -> list[Any] | dict[str, Any]:
        raise NotImplementedError

    @abstractmethod
    async def request_text(
        self,
        url: str,
        *,
        content_type: str,
        **kwargs: Any,
    ) -> str:
        raise NotImplementedError
