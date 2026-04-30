import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import json
import uuid
import logging
from datetime import datetime, UTC

import uvicorn
from fastapi import FastAPI, Query, Depends, Request, HTTPException, status
from fastapi.encoders import jsonable_encoder
from contextlib import asynccontextmanager
from redis.asyncio import Redis

from app.db.session import engine, async_session_maker
from app.models.base import Base
from app.schemas.trip import TripRead
from app.db.seed import seed_trips, reset_db
from app.services.search import get_trips_from_providers
from app.services.ranking import rank_trips
from app.core.redis import get_redis
from app.core.dependencies import create_rate_limit_dependency

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("logs/rate_limiter.log"),
    ],
)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    redis = get_redis()
    await redis.ping()
    logger.info("Redis connected")

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with async_session_maker() as session:
        await seed_trips(session)

    yield

    await redis.aclose()
    await engine.dispose()
    logger.info("Redis disconnected")


app = FastAPI(
    title="Travel Aggregator API",
    version="0.1.0",
    lifespan=lifespan,
)


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


search_rate_limit = create_rate_limit_dependency("/search", 5, 30)
debug_rate_limit = create_rate_limit_dependency("/debug/reset-db", 3, 60)


@app.get("/search", response_model=list[TripRead], dependencies=[Depends(search_rate_limit)])
async def search_trips(
    destination: str = Query(..., min_length=1),
    max_price: float | None = None,
    redis: Redis = Depends(get_redis),
):
    cache_key = f"search:{destination}:{max_price if max_price else 'none'}"

    # Try cache
    try:
        cached = await redis.get(cache_key)
        if cached:
            return [TripRead(**item) for item in json.loads(cached)]
    except Exception:
        pass

    results = await get_trips_from_providers()

    all_trips = []
    for trips in results.values():
        all_trips.extend(trips)

    filtered = [t for t in all_trips if t["destination"] == destination]
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
    try:
        await redis.setex(
            cache_key,
            60,
            json.dumps(jsonable_encoder(response))
        )
    except Exception:
        pass

    return response


@app.post("/debug/reset-db", dependencies=[Depends(debug_rate_limit)])
async def debug_reset_db():
    async with async_session_maker() as session:
        await reset_db(session)
        await seed_trips(session)
    return {"status": "database reset"}


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)