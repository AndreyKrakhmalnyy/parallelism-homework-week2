from app.infrastructure.queues.types import EventViewQueue
from app.infrastructure.redis.manager import RedisManager
from app.infrastructure.queues.producers.base import BaseQueueProducer


class EventQueueProducer(BaseQueueProducer):
    EVENT_VIEW_UNIQ_CACHE = 5 * 60 # 5 min

    def __init__(self, queue: EventViewQueue, redis_manager: RedisManager) -> None:
        super().__init__(queue)
        self.redis = redis_manager

    async def record_view(self, event_id: int, ip_address: str) -> None:
        key = f"event_view:{event_id}:{ip_address}"
        is_setted = await self.redis.client.set(
            name=key, value=str(event_id), nx=True, ex=self.EVENT_VIEW_UNIQ_CACHE
        )  # 5 min
        if is_setted:
            await self.put(event_id)
