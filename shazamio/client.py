from types import SimpleNamespace
from typing import Any, Optional, List, Dict, Union

from aiohttp import ClientSession, TraceRequestStartParams, TraceConfig
from aiohttp_retry import RetryClient, RetryOptionsBase

from shazamio.exceptions import BadMethod, FailedDecodeJson
from shazamio.interfaces.client import HTTPClientInterface
from shazamio.loggers import request as request_logger
from shazamio.utils import validate_json


class HTTPClient(HTTPClientInterface):
    def __init__(self, retry_options: Optional[RetryOptionsBase] = None):
        self.retry_options = retry_options
        self.trace_config = TraceConfig()
        self.trace_config.on_request_start.append(self.on_request_start)

    async def on_request_start(
        self,
        _: ClientSession,
        trace_config_ctx: SimpleNamespace,
        params: TraceRequestStartParams,
    ) -> None:
        current_attempt = trace_config_ctx.trace_request_ctx["current_attempt"]
        request_logger.debug(
            "Sending HTTP request",
            extra={
                "url": params.url,
                "method": params.method,
                "headers": params.headers,
                "attempt": current_attempt,
                "attempts": self.retry_options.attempts,
            },
        )

    async def request(
        self,
        method: str,
        url: str,
        *args,
        **kwargs,
    ) -> Union[List[Any], Dict[str, Any]]:
        async with RetryClient(
            retry_options=self.retry_options,
            raise_for_status=False,
            trace_configs=[self.trace_config],
        ) as client:
            if method.upper() == "GET":
                async with client.get(url, **kwargs) as resp:
                    try:
                        return await validate_json(resp, *args)
                    except FailedDecodeJson as e:
                        raise e

            elif method.upper() == "POST":
                async with client.post(url, **kwargs) as resp:
                    try:
                        return await validate_json(resp, *args)
                    except FailedDecodeJson as e:
                        raise e
            else:
                raise BadMethod("Accept only GET/POST")
