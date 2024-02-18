from abc import ABC, abstractmethod
from typing import Any, List, Dict


class HTTPClientInterface(ABC):
    @abstractmethod
    async def request(
        self,
        method: str,
        url: str,
        *args,
        **kwargs,
    ) -> List[Any] | Dict[str, Any]:
        raise NotImplementedError
