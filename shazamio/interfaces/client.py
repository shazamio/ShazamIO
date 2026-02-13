from abc import ABC, abstractmethod
from typing import Any, List, Dict, Union


class HTTPClientInterface(ABC):
    @abstractmethod
    async def request(
        self,
        method: str,
        url: str,
        *args,
        **kwargs,
    ) -> Union[List[Any], Dict[str, Any]]:
        raise NotImplementedError

    async def request_csv(
        self,
        url: str,
        **kwargs,
    ) -> Dict[str, Any]:
        raise NotImplementedError
