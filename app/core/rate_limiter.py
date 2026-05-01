import random
import logging
from time import time
from redis.asyncio import Redis

logger = logging.getLogger(__name__)


class RateLimiter:
    def __init__(self, redis: Redis):
        self._redis = redis
        self._lua_sha = None

    async def _load_script(self):
        if self._lua_sha is None:
            script = """
                redis.call("ZREMRANGEBYSCORE", KEYS[1], 0, ARGV[2])
                local count = redis.call("ZCARD", KEYS[1])
                if count >= tonumber(ARGV[3]) then
                    return 1
                end
                redis.call("ZADD", KEYS[1], ARGV[1], ARGV[5])
                redis.call("EXPIRE", KEYS[1], ARGV[4])
                return 0
            """
            self._lua_sha = await self._redis.script_load(script)

    async def is_limited(
        self,
        ip_address: str,
        endpoint: str,
        max_requests: int,
        window_seconds: int,
    ) -> bool:
        await self._load_script()
        key = f"rate_limiter:{endpoint}:{ip_address}"
        current_ms = int(time() * 1000)
        window_start_ms = current_ms - window_seconds * 1000
        member_id = f"{current_ms}-{random.randint(0, 100_000)}"
        result = await self._redis.evalsha(
            self._lua_sha,
            1,
            key,
            current_ms,
            window_start_ms,
            max_requests,
            window_seconds,
            member_id,
        )
        if result == 1:
            logger.warning(f"Rate limit exceeded for {ip_address} on {endpoint}")
        return result == 1