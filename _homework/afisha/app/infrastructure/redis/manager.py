from collections.abc import Awaitable
import random
from typing import Any, Callable
from pydantic import BaseModel
from redis.asyncio import Redis
from redis.exceptions import LockError
from app.config import RedisConfig


class RedisManager:
    def __init__(self, redis: Redis) -> None:
        self.client = redis
    
    async def close(self) -> None:
        await self.client.aclose()
    
    async def get_or_set_with_lock(
        self,
        ttl: int,
        cache_key: str,
        dto: BaseModel,
        fetch: Callable[[], Awaitable[Any]],
        error_cls: Exception,
        timeout: int = 5,
        blocking_timeout: int = 3,
    ):
        cached_data = await self.client.get(cache_key)

        if cached_data:
            return dto.model_validate_json(cached_data)
        
        try:
            async with self.client.lock(
                name=f"lock:{cache_key}",
                timeout=timeout,
                blocking_timeout=blocking_timeout,
            ):
                cached_data = await self.client.get(cache_key)

                if cached_data:
                    return dto.model_validate_json(cached_data)
                raw_data = await fetch()
                db_data = dto.model_validate(raw_data)
                await self.client.set(
                    name=cache_key,
                    value=db_data.model_dump_json(),
                    ex=self._ttl_jitter(ttl)
                )
                return db_data
        except LockError:
            raise error_cls
    
    def _ttl_jitter(self, ttl: int) -> float:
        delay = min(30, max(1, ttl // 2))
        return max(1, ttl + random.randint(-delay, delay))

def create_redis_manager(redis_conf: RedisConfig) -> RedisManager:
    redis = Redis.from_url(
        redis_conf.url,
        decode_responses=True
    )
    return RedisManager(redis)