import logging

from fastapi import APIRouter

from app.db.session import async_session_maker
from app.db.seed import seed_trips, reset_db
from app.api.deps import debug_rate_limit

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/debug", tags=["debug"])


@router.post("/reset-db", dependencies=[debug_rate_limit])
async def debug_reset_db():
    async with async_session_maker() as session:
        await reset_db(session)
        await seed_trips(session)
    return {"status": "database reset"}
