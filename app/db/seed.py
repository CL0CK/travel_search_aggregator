from sqlalchemy import select, func, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.trip import Trip


async def seed_trips(session: AsyncSession) -> None:
    count = await session.scalar(select(func.count(Trip.id)))
    if count > 0:
        return

    trips = [
        Trip(destination="Paris", price=420.0, rating=4.5, provider="ProviderA"),
        Trip(destination="Barcelona", price=380.0, rating=4.3, provider="ProviderB"),
        Trip(destination="Rome", price=450.0, rating=4.7, provider="ProviderA"),
        Trip(destination="London", price=520.0, rating=4.6, provider="ProviderC"),
        Trip(destination="Berlin", price=320.0, rating=4.1, provider="ProviderB"),
    ]
    session.add_all(trips)
    await session.commit()


async def reset_db(session: AsyncSession) -> None:
    await session.execute(delete(Trip))
    await session.commit()