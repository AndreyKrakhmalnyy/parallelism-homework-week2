import asyncio
import random
import httpx
from httpx import AsyncClient, Response
from typing import Optional


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
        )

    async def close_connection(self) -> None:
        await self.client.aclose()

    async def request(
            self, 
            method: str, 
            url: str,
            retry: bool = False,
            **kwargs
        ) -> Response:
        if retry:
            for attempt in range(self.retry_count):
                try:
                    response = await self.client.request(method, url, **kwargs)
                except (httpx.NetworkError, httpx.TimeoutException):
                    if (is_last_attempt := attempt == attempt - 1):
                        raise
                await self._exponential_backoff_sleep(attempt)
                continue
            if response.status_code not in (409, 500, 503) or is_last_attempt:
                return response
            self._exponential_backoff_sleep(attempt)

    async def _exponential_backoff_sleep(self, attempt: int) -> None:
        delay = 0.5 ** (attempt + 1)  
        jitter = random.uniform(0.1, 0.4)
        await asyncio.sleep(delay + jitter)
