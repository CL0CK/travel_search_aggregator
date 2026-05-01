import logging
from fastapi import Request, HTTPException, status, Depends

logger = logging.getLogger(__name__)


def create_rate_limit_dependency(
    endpoint: str,
    max_requests: int,
    window_seconds: int,
):
    async def dependency(request: Request):
        rate_limiter = getattr(request.app.state, "rate_limiter", None)
        if rate_limiter is None:
            return  # Skip rate limiting if not initialized (e.g., tests)
        x_forwarded_for = request.headers.get("X-Forwarded-For")
        ip_address = x_forwarded_for.split(",")[0] if x_forwarded_for else request.client.host
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
                detail="Request limit exceeded",
                headers={"Retry-After": str(retry_after)},
            )
    return dependency