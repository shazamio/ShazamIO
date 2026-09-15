from types import SimpleNamespace
from typing import Any

from aiohttp import ClientSession, TraceConfig, TraceRequestStartParams
from aiohttp_retry import ExponentialRetry, RetryClient, RetryOptionsBase

from shazamio.exceptions import BadMethod
from shazamio.interfaces.client import HTTPClientInterface
from shazamio.loggers import request as request_logger
from shazamio.utils import validate_json


class HTTPClient(HTTPClientInterface):
    def __init__(self, retry_options: RetryOptionsBase | None = None) -> None:
        # `HTTPClient()` used to die in the tracer below, which reads `.attempts`:
        #  `AttributeError: 'NoneType' object has no attribute 'attempts'`.
        #  `RetryClient` falls back to this very default, so no request changes:
        #  https://github.com/inyutin/aiohttp_retry/blob/39b23915023dde0e0298b822de3d23960a5024e6/aiohttp_retry/client.py#L210
        self.retry_options: RetryOptionsBase = retry_options or ExponentialRetry()
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
        **kwargs: Any,
    ) -> list[Any] | dict[str, Any]:
        async with RetryClient(
            retry_options=self.retry_options,
            raise_for_status=False,
            trace_configs=[self.trace_config],
        ) as client:
            if method.upper() == "GET":
                async with client.get(url, **kwargs) as response:
                    return await validate_json(response)

            if method.upper() == "POST":
                async with client.post(url, **kwargs) as response:
                    return await validate_json(response)

            msg: str = "Accept only GET/POST"
            raise BadMethod(msg)

    async def request_text(
        self,
        url: str,
        **kwargs: Any,
    ) -> str:
        """Fetch a body no JSON decoder should see, such as the chart CSV."""
        async with (
            RetryClient(
                retry_options=self.retry_options,
                raise_for_status=True,
                trace_configs=[self.trace_config],
            ) as client,
            client.get(url, **kwargs) as response,
        ):
            return await response.text()
