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
from app.schemas.search_ai import SearchAIRequest, SearchAIResponse
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
        logger.warning(f"LLM model not available, /search_ai will be disabled: {e}")

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
search_ai_rate_limit = create_rate_limit_dependency("/search_ai", 3, 60)


@app.get("/search", response_model=list[TripRead], dependencies=[Depends(search_rate_limit)])
async def search_trips(
    destination: str = Query(..., min_length=1),
    origin: str = Query(..., min_length=1),
    check_in: str = Query(..., description="ISO date: 2026-05-11"),
    check_out: str = Query(..., description="ISO date: 2026-05-18"),
    max_price: float | None = None,
    hotel_stars: int | None = None,
    mock: bool = Query(True, description="True = mock data, False = RapidAPI real data"),
    cache: CacheService = Depends(get_cache_service),
):
    destination = destination.lower()
    origin = origin.lower()
    max_price = round(max_price, 2) if max_price else None
    stars_filter = hotel_stars if hotel_stars else "none"
    cache_key = f"v1:search:{origin}:{destination}:{check_in}:{check_out}:{max_price if max_price else 'none'}:{stars_filter}:{'mock' if mock else 'real'}"

    # Try cache
    cached = await cache.get(cache_key)
    if cached:
        return [TripRead(**item) for item in cached]

    results = await get_trips_from_providers(
        mock=mock,
        origin=origin,
        destination=destination,
        check_in=check_in,
        check_out=check_out,
        hotel_stars=hotel_stars,
    )

    all_trips = []
    for trips in results.values():
        all_trips.extend(trips)

    if mock:
        filtered = [t for t in all_trips if t["destination"].lower() == destination]
    else:
        filtered = list(all_trips)
    if max_price is not None:
        filtered = [t for t in filtered if t["price"] <= max_price]
    if hotel_stars is not None:
        filtered = [t for t in filtered if t.get("hotel_stars") == hotel_stars]

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
            origin=t.get("origin"),
            hotel_stars=t.get("hotel_stars"),
            flight_price=t.get("flight_price"),
            hotel_price=t.get("hotel_price"),
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


@app.post("/search_ai", response_model=SearchAIResponse, dependencies=[Depends(search_ai_rate_limit)])
async def search_trips_ai(
    body: SearchAIRequest,
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

    # Validate required fields
    if not extracted.destination:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not determine destination. Please specify a city.",
        )
    if not extracted.origin:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Please specify your departure city.",
        )
    if not extracted.check_in or not extracted.check_out:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Please specify your travel dates.",
        )

    destination = extracted.destination.lower()
    origin = extracted.origin.lower()
    budget = round(extracted.budget, 2) if extracted.budget else None
    check_in = extracted.check_in
    check_out = extracted.check_out
    cache_key = f"v1:search_ai:{origin}:{destination}:{check_in}:{check_out}:{budget if budget else 'none'}:{'mock' if body.mock else 'real'}"

    # Try cache
    cached = await cache.get(cache_key)
    if cached:
        return SearchAIResponse(**cached)

    # Search providers
    results = await get_trips_from_providers(
        mock=body.mock,
        origin=origin,
        destination=destination,
        check_in=check_in,
        check_out=check_out,
        hotel_stars=None,
    )
    all_trips = []
    for trips in results.values():
        all_trips.extend(trips)

    filtered = list(all_trips) if not body.mock else [t for t in all_trips if t["destination"].lower() == destination]
    if budget is not None:
        filtered = [t for t in filtered if t["price"] <= budget]

    ranked = rank_trips(filtered, budget)

    now = datetime.now(UTC)
    response_data = SearchAIResponse(
        destination=destination,
        origin=origin,
        budget=budget,
        results=[
            TripRead(
                id=uuid.uuid4(),
                destination=t["destination"],
                price=t["price"],
                rating=t["rating"],
                provider=t["provider"],
                created_at=now,
                origin=t.get("origin"),
                hotel_stars=t.get("hotel_stars"),
                flight_price=t.get("flight_price"),
                hotel_price=t.get("hotel_price"),
            )
            for t in ranked
        ],
    )

    # Cache the response
    await cache.set(cache_key, response_data)
    return response_data


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)