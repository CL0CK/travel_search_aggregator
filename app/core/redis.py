from redis.asyncio import Redis
from functools import lru_cache


@lru_cache
def get_redis() -> Redis:
    return Redis(host="localhost", port=6379)