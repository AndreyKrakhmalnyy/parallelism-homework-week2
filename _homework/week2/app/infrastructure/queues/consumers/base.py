from abc import ABC, abstractmethod
import asyncio
from typing import Optional


class BaseQueueConsumer(ABC):
    def __init__(self, queue: asyncio.Queue) -> None:
        self._task: Optional[asyncio.Task] = None
        self.queue = queue

    def start(self) -> None:
        self._task = asyncio.create_task(self._run())

    async def stop(self) -> None:
        if self._task is None: return

        self._task.cancel()

        try:
            await self._task
            
        except asyncio.CancelledError:
            pass

    @abstractmethod
    async def _run(self) -> None:
        pass