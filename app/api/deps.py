import logging
from fastapi import Request, Depends
from redis.asyncio import Redis

from app.core.redis import create_redis
from app.core.dependencies import create_rate_limit_dependency
from app.core.config import settings
from app.services.cache import CacheService

logger = logging.getLogger(__name__)


def get_redis(request: Request) -> Redis:
    redis = getattr(request.app.state, "redis", None)
    if redis is None:
        return create_redis()
    return redis


def get_cache_service(request: Request) -> CacheService:
    cache = getattr(request.app.state, "cache_service", None)
    if cache is None:
        redis = get_redis(request)
        return CacheService(redis, ttl=settings.cache_ttl)
    return cache


search_rate_limit = Depends(
    create_rate_limit_dependency("/search", settings.rate_limit_max_requests, settings.rate_limit_window_seconds)
)

search_ai_rate_limit = Depends(
    create_rate_limit_dependency("/search_ai", 3, 60)
)

debug_rate_limit = Depends(
    create_rate_limit_dependency("/debug/reset-db", 3, 60)
)
