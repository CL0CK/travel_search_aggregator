from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession, AsyncEngine

from app.core.config import settings


def _get_engine() -> AsyncEngine:
    if not settings.has_db:
        raise RuntimeError("DATABASE_URL not configured")
    return create_async_engine(settings.database_url, echo=False)


def _get_session_maker(engine: AsyncEngine):
    return async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


# Lazy engine - created only when accessed
_engine = None
_session_maker = None


def get_engine():
    global _engine
    if _engine is None:
        _engine = _get_engine()
    return _engine


def get_session_maker():
    global _session_maker
    if _session_maker is None:
        _session_maker = _get_session_maker(get_engine())
    return _session_maker


async def get_session():
    async with get_session_maker()() as session:
        yield session
