from redis.asyncio import Redis

from app.config import RedisConfig


class RedisManager:
    def __init__(self, redis: Redis) -> None:
        self.client = redis
    
    async def close(self) -> None:
        await self.client.aclose()
    


def create_redis_manager(redis_conf: RedisConfig) -> RedisManager:
    redis = Redis.from_url(
        redis_conf.url,
        decode_responses=True
    )
    return RedisManager(redis)