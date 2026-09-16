from http import HTTPStatus
from types import SimpleNamespace, TracebackType
from typing import Any

from aiohttp import ClientSession, TraceConfig, TraceRequestStartParams
from aiohttp_retry import ExponentialRetry, RetryClient, RetryOptionsBase

from shazamio.exceptions import BadContentType, BadMethod, BadResponseStatus
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
        self._retry_client: RetryClient | None = None

    # `typing.Self` arrived in 3.11 and the floor is 3.10, so the class names
    #  itself here.
    async def __aenter__(self) -> "HTTPClient":  # noqa: PYI034
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        await self.close()

    async def close(self) -> None:
        """Close the pooled connections. A request after this raises `RuntimeError`."""
        if self._retry_client is not None:
            await self._retry_client.close()

    def _ensure_client(self) -> RetryClient:
        # Built on the first request rather than in `__init__`: a `ClientSession`
        #  binds to whichever loop is running when it is constructed, and the
        #  documented usage builds a `Shazam` outside `asyncio.run` and awaits it
        #  inside. One client means one session, which is what pools connections.
        if self._retry_client is None:
            self._retry_client = RetryClient(
                retry_options=self.retry_options,
                raise_for_status=False,
                trace_configs=[self.trace_config],
            )

        return self._retry_client

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
        client = self._ensure_client()

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
        *,
        content_type: str,
        **kwargs: Any,
    ) -> str:
        """Fetch a body no JSON decoder should see, such as the chart CSV."""
        client = self._ensure_client()

        async with client.get(url, **kwargs) as response:
            if response.status != HTTPStatus.OK:
                msg = f"{url} answered {response.status}"
                raise BadResponseStatus(msg)

            # A path the edge does not route to the API is answered by the website
            #  itself, `200 text/html`, so the status alone says nothing about the
            #  body. Without this the caller gets a parse error naming the parser.
            if response.content_type != content_type:
                msg = f"{url} answered {response.content_type}, expected {content_type}"
                raise BadContentType(msg)

            return await response.text()
