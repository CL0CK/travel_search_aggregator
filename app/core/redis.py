from redis.asyncio import Redis

from app.core.config import settings


def create_redis() -> Redis:
    url = settings.redis_url
    if url.startswith("https://"):
        url = "redis://" + url[8:]
    return Redis.from_url(
        url,
        decode_responses=True,
        socket_timeout=5,
        socket_connect_timeout=5,
        max_connections=10,
    )