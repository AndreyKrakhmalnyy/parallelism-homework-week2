import asyncio
from collections import defaultdict
import logging
import time

from dishka import AsyncContainer
from app.infrastructure.exceptions import EventViewConsumeringError
from app.infrastructure.queues.types import EventViewQueue
from app.infrastructure.queues.consumers.base import BaseQueueConsumer
from app.infrastructure.postgres.models import EventView
from app.infrastructure.postgres.manager import DatabaseManager

logger = logging.getLogger(__name__)


class EventViewQueueConsumer(BaseQueueConsumer):
    FLUSH_TIMEOUT = 5.0  # таймаут для очереди
    FLUSH_COUNT = 10  # макс число мероприятий для пуша в бд

    def __init__(self, queue: EventViewQueue, container: AsyncContainer) -> None:
        super().__init__(queue)
        self.container = container
        self.agg_store = defaultdict(int)

    async def _run(self) -> None:
        deadline = time.monotonic() + self.FLUSH_TIMEOUT

        try:
            while True:
                try:
                    event_id = await asyncio.wait_for(
                        self.queue.get(),
                        timeout=max(0.0, deadline - time.monotonic()),
                    )
                    self.agg_store[event_id] += 1
                except asyncio.TimeoutError:
                    pass

                if (
                    sum(self.agg_store.values()) >= self.FLUSH_COUNT
                    or time.monotonic() >= deadline
                ):
                    await self._flush()
                    deadline = time.monotonic() + self.FLUSH_TIMEOUT

        except asyncio.CancelledError:
            try:
                await self._flush()
            except EventViewConsumeringError as e:
                logger.error(str(e))
            raise

    async def _flush(self) -> None:
        if not self.agg_store:
            return
        try:
            async with self.container() as request_container:
                db_manager = await request_container.get(DatabaseManager)
                await db_manager.event_repo.add_event_views_bulk(
                    [
                        EventView(event_id=event_id, views_count=views_count)
                        for event_id, views_count in self.agg_store.items()
                    ]
                )
                await db_manager.commit()
        except Exception as e:
            raise EventViewConsumeringError(str(e)) from e
        self.agg_store.clear()
