import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import uuid
import logging
from datetime import datetime, UTC

import uvicorn
from fastapi import FastAPI, Query, Depends, Request, HTTPException, status
from contextlib import asynccontextmanager
from redis.asyncio import Redis

from app.db.session import engine, async_session_maker
from app.models.base import Base
from app.schemas.trip import TripRead
from app.schemas.recommend import RecommendRequest, RecommendResponse
from app.db.seed import seed_trips, reset_db
from app.services.search import get_trips_from_providers
from app.services.ranking import rank_trips
from app.services.cache import CacheService
from app.services.llm import extract_travel_params
from app.services.model_download import ensure_model_available
from app.core.redis import create_redis
from app.core.rate_limiter import RateLimiter
from app.core.dependencies import create_rate_limit_dependency
from app.core.config import settings

import io

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(stream=io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")),
        logging.FileHandler("logs/rate_limiter.log", encoding="utf-8"),
    ],
)

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


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        ensure_model_available()
    except Exception as e:
        logger.warning(f"LLM model not available, /recommend will be disabled: {e}")

    redis = None
    try:
        redis = create_redis()
        await redis.ping()
        logger.info("Redis connected")
        app.state.redis = redis
        app.state.rate_limiter = RateLimiter(redis)
        app.state.cache_service = CacheService(redis, ttl=settings.cache_ttl)
    except Exception as e:
        logger.warning(f"Redis unavailable, running without cache/rate limiting: {e}")

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with async_session_maker() as session:
        await seed_trips(session)

    yield

    if redis:
        await redis.aclose()
        logger.info("Redis disconnected")
    await engine.dispose()


app = FastAPI(
    title="Travel Aggregator API",
    version="0.2.0",
    lifespan=lifespan,
)


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


search_rate_limit = create_rate_limit_dependency("/search", settings.rate_limit_max_requests, settings.rate_limit_window_seconds)
debug_rate_limit = create_rate_limit_dependency("/debug/reset-db", 3, 60)
recommend_rate_limit = create_rate_limit_dependency("/recommend", 3, 60)


@app.get("/search", response_model=list[TripRead], dependencies=[Depends(search_rate_limit)])
async def search_trips(
    destination: str = Query(..., min_length=1),
    max_price: float | None = None,
    cache: CacheService = Depends(get_cache_service),
):
    destination = destination.lower()
    max_price = round(max_price, 2) if max_price else None
    cache_key = f"v1:search:{destination}:{max_price if max_price else 'none'}"

    # Try cache
    cached = await cache.get(cache_key)
    if cached:
        return [TripRead(**item) for item in cached]

    results = await get_trips_from_providers()

    all_trips = []
    for trips in results.values():
        all_trips.extend(trips)

    filtered = [t for t in all_trips if t["destination"].lower() == destination]
    if max_price is not None:
        filtered = [t for t in filtered if t["price"] <= max_price]

    ranked_trips = rank_trips(filtered, max_price)

    now = datetime.now(UTC)
    response = [
        TripRead(
            id=uuid.uuid4(),
            destination=t["destination"],
            price=t["price"],
            rating=t["rating"],
            provider=t["provider"],
            created_at=now,
        )
        for t in ranked_trips
    ]

    # Store in cache
    await cache.set(cache_key, response)

    return response


@app.post("/debug/reset-db", dependencies=[Depends(debug_rate_limit)])
async def debug_reset_db():
    async with async_session_maker() as session:
        await reset_db(session)
        await seed_trips(session)
    return {"status": "database reset"}


@app.post("/recommend", response_model=RecommendResponse, dependencies=[Depends(recommend_rate_limit)])
async def recommend_trips(
    body: RecommendRequest,
    cache: CacheService = Depends(get_cache_service),
):
    # Extract params using Ollama
    try:
        extracted = await extract_travel_params(body.query)
    except Exception as e:
        logger.error(f"LLM extraction failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process query with AI",
        )

    destination = extracted.destination.lower()
    budget = round(extracted.budget, 2) if extracted.budget else None
    cache_key = f"v1:recommend:{destination}:{budget if budget else 'none'}"

    # Try cache
    cached = await cache.get(cache_key)
    if cached:
        return RecommendResponse(**cached)

    # Search providers
    results = await get_trips_from_providers()
    all_trips = []
    for trips in results.values():
        all_trips.extend(trips)

    filtered = [t for t in all_trips if t["destination"].lower() == destination]
    if budget is not None:
        filtered = [t for t in filtered if t["price"] <= budget]

    ranked = rank_trips(filtered, budget)

    now = datetime.now(UTC)
    response_data = RecommendResponse(
        destination=destination,
        budget=budget,
        results=[
            TripRead(
                id=uuid.uuid4(),
                destination=t["destination"],
                price=t["price"],
                rating=t["rating"],
                provider=t["provider"],
                created_at=now,
            )
            for t in ranked
        ],
    )

    # Cache the response
    await cache.set(cache_key, response_data)
    return response_data


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)