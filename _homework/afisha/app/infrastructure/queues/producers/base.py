import asyncio
from abc import ABC


class BaseQueueProducer(ABC):
    def __init__(self, queue: asyncio.Queue) -> None:
        self._queue = queue

    async def put(self, item) -> None:
        await self._queue.put(item)
