import asyncio
from collections.abc import Awaitable, Callable
import random
from typing import Any

from pydantic import BaseModel
from redis.exceptions import LockError

from app.infrastructure.redis.manager import RedisManager

import random


class CacheManager:
    BASE_TTL_DELAY = 30 # 30 sec

    def __init__(self, redis_manager: RedisManager) -> None:
        self.redis_manager = redis_manager.client

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
        cached_data = await self.redis_manager.get(cache_key)

        if cached_data:
            return dto.model_validate_json(cached_data)
        
        try:
            async with self.redis_manager.lock(
                name=f"lock:{cache_key}",
                timeout=timeout,
                blocking_timeout=blocking_timeout,
            ):
                cached_data = await self.redis_manager.get(cache_key)

                if cached_data:
                    return dto.model_validate_json(cached_data)
                raw_data = await fetch()
                db_data = dto.model_validate(raw_data)
                await self.redis_manager.set(
                    name=cache_key,
                    value=db_data.model_dump_json(),
                    ex=self._ttl_jitter(ttl)
                )
                return db_data
        except LockError:
            raise error_cls


    def _ttl_jitter(self, ttl: int) -> float:
        return ttl + random.randint(-self.BASE_TTL_DELAY, self.BASE_TTL_DELAY)