import logging
import orjson
import asyncio
from fastapi.encoders import jsonable_encoder
from redis.asyncio import Redis

logger = logging.getLogger(__name__)


class CacheService:
    def __init__(self, redis: Redis, ttl: int = 60):
        self.redis = redis
        self.ttl = ttl

    async def _with_timeout(self, coro, timeout: float = 0.5):
        try:
            return await asyncio.wait_for(coro, timeout=timeout)
        except (asyncio.TimeoutError, Exception) as e:
            logger.debug(f"Cache operation failed: {e}")
            return None

    async def get(self, key: str):
        result = await self._with_timeout(self.redis.get(key))
        if result:
            logger.info(f"Cache hit: {key}")
            try:
                return orjson.loads(result)
            except Exception:
                return None
        logger.info(f"Cache miss: {key}")
        return None

    async def set(self, key: str, value: any):
        try:
            serialized = orjson.dumps(jsonable_encoder(value))
            await self._with_timeout(self.redis.setex(key, self.ttl, serialized))
        except Exception as e:
            logger.debug(f"Redis cache set error: {e}")