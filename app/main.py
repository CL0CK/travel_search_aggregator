from fastapi import FastAPI
from contextlib import asynccontextmanager

from app.db.session import engine, async_session_maker
from app.models.base import Base
from app.db.seed import seed_trips, reset_db


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