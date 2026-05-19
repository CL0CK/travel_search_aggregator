import sys
import io
import logging
import os
from pathlib import Path
from contextlib import asynccontextmanager

sys.path.insert(0, str(Path(__file__).parent.parent))

# Create logs directory if it doesn't exist
os.makedirs("logs", exist_ok=True)

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.redis import create_redis
from app.core.rate_limiter import RateLimiter
from app.services.cache import CacheService
from app.services.model_download import ensure_model_available
from app.db.session import get_engine, get_session_maker
from app.models.base import Base
from app.db.seed import seed_trips

from app.api.routes.health import router as health_router
from app.api.routes.search import router as search_router
from app.api.routes.search_ai import router as search_ai_router
from app.api.routes.debug import router as debug_router
from app.api.routes.extract import router as extract_router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(stream=io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")),
        logging.FileHandler("logs/rate_limiter.log", encoding="utf-8"),
    ],
)

logger = logging.getLogger(__name__)


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

    if settings.has_db:
        try:
            engine = get_engine()
            async with engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
            session_maker = get_session_maker()
            async with session_maker() as session:
                await seed_trips(session)
            logger.info("PostgreSQL connected and seeded")
        except Exception as e:
            logger.warning(f"PostgreSQL unavailable: {e}")
    else:
        logger.info("PostgreSQL not configured, running without database")

    yield

    if redis:
        await redis.aclose()
        logger.info("Redis disconnected")
    if settings.has_db:
        await get_engine().dispose()


app = FastAPI(
    title="Travel Aggregator API",
    version="0.2.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router)
app.include_router(search_router)
app.include_router(search_ai_router)
app.include_router(debug_router)
app.include_router(extract_router)

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
