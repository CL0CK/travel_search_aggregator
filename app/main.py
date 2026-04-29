import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import uuid
from datetime import datetime, UTC

import uvicorn
from fastapi import FastAPI, Query
from contextlib import asynccontextmanager

from app.db.session import engine, async_session_maker
from app.models.base import Base
from app.schemas.trip import TripRead
from app.db.seed import seed_trips, reset_db
from app.services.search import get_trips_from_providers


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with async_session_maker() as session:
        await seed_trips(session)

    yield
    await engine.dispose()


app = FastAPI(
    title="Travel Aggregator API",
    version="0.1.0",
    lifespan=lifespan,
)


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


@app.post("/debug/reset-db")
async def debug_reset_db():
    async with async_session_maker() as session:
        await reset_db(session)
        await seed_trips(session)
    return {"status": "database reset"}


@app.get("/search", response_model=list[TripRead])
async def search_trips(
    destination: str = Query(..., min_length=1),
    max_price: float | None = None,
):
    results = await get_trips_from_providers()

    all_trips = []
    for trips in results.values():
        all_trips.extend(trips)

    filtered = [t for t in all_trips if t["destination"] == destination]
    if max_price is not None:
        filtered = [t for t in filtered if t["price"] <= max_price]

    now = datetime.now(UTC)
    return [
        TripRead(
            id=uuid.uuid4(),
            destination=t["destination"],
            price=t["price"],
            rating=t["rating"],
            provider=t["provider"],
            created_at=now,
        )
        for t in filtered
    ]

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)