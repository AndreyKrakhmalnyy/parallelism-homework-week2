import asyncio
import logging
import random
import time
import httpx
from httpx import AsyncClient, Response
from typing import Optional


logger = logging.getLogger("samokat.httpx")


async def on_request(request: httpx.Request) -> None:
    request.extensions["started_at"] = time.perf_counter()


async def on_response(response: httpx.Response) -> None:
    started_at = response.request.extensions.get("started_at")
    duration = time.perf_counter() - started_at if started_at is not None else 0

    logger.info(
        "HTTP request completed: method=%s url=%s status=%s duration=%.3fs",
        response.request.method,
        response.request.url,
        response.status_code,
        duration,
    )

class BaseHTTPConnector:
    def __init__(
        self,
        base_url: str,
        timeout: float,
        retry_count: int,
        headers: Optional[dict[str, str]] = None
    ) -> None:
        self.retry_count = retry_count
        self.client = AsyncClient(
            base_url=base_url,
            timeout=timeout,
            headers=headers,
            event_hooks={
                "request": [on_request],
                "response": [on_response],
            },
        )

    async def close_connection(self) -> None:
        await self.client.aclose()

    async def request(
            self, 
            method: str, 
            url: str,
            retry: bool = False,
            **kwargs
        ) -> Optional[Response]:
        if not retry:
            response = await self.client.request(method, url, **kwargs)
            response.raise_for_status()
            return response
        
        for attempt in range(self.retry_count):
            is_last_attempt = attempt == self.retry_count - 1
            try:
                response = await self.client.request(method, url, **kwargs)
            except (httpx.NetworkError, httpx.TimeoutException):
                if is_last_attempt:
                    raise
                await self._exponential_backoff_sleep(attempt)
                continue
            
        if response.status_code not in (409, 429, 500, 503) or is_last_attempt:
            return response
        await self._exponential_backoff_sleep(attempt)

    async def _exponential_backoff_sleep(self, attempt: int) -> None:
        delay = 0.5 ** (attempt + 1)  
        jitter = random.uniform(0.1, 0.4)
        await asyncio.sleep(delay + jitter)
