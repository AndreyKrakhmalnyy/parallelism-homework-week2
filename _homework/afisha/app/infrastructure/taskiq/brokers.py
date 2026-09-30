from app.config import settings
from taskiq_redis import RedisStreamBroker
from taskiq.middlewares import SimpleRetryMiddleware
from taskiq.schedule_sources import LabelScheduleSource
from taskiq import TaskiqScheduler


asyncio_broker = RedisStreamBroker(
    url=settings.redis.url,
    queue_name="asyncio_queue",
    socket_timeout=None
).with_middlewares(SimpleRetryMiddleware(types_of_exceptions=(Exception,)),)

scheduler = TaskiqScheduler(
    broker=asyncio_broker,
    sources=[LabelScheduleSource(broker=asyncio_broker)],
)

cpu_broker = RedisStreamBroker(
    url=settings.redis.url,
    queue_name="cpu_queue",
    socket_timeout=None,
    xread_count=1,
).with_middlewares(SimpleRetryMiddleware(types_of_exceptions=(Exception,)),)
