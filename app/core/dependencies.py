import logging
from fastapi import Request, HTTPException, status, Depends
from app.core.rate_limiter import RateLimiter, get_rate_limiter

logger = logging.getLogger(__name__)


def create_rate_limit_dependency(
    endpoint: str,
    max_requests: int,
    window_seconds: int,
):
    async def dependency(
        request: Request,
        rate_limiter: RateLimiter = Depends(get_rate_limiter),
    ):
        ip_address = request.client.host
        limited = await rate_limiter.is_limited(
            ip_address, endpoint, max_requests, window_seconds
        )
        if limited:
            retry_after = window_seconds
            logger.warning(
                f"Rate limit exceeded for {ip_address} on {endpoint}"
            )
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Превышено количество запросов",
                headers={"Retry-After": str(retry_after)},
            )
    return dependency