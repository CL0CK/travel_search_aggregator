import asyncio

from app.providers.adapters import adapt_trips, MAPPING_A
from app.schemas.trip import TripDTO


async def provider_a() -> list[TripDTO]:
    """Provider A - Clean API format."""
    await asyncio.sleep(0.3)

    raw_trips = [
        {"id": "a1", "destination": "Paris", "price": 420.0, "rating": 4.5},
        {"id": "a2", "destination": "Barcelona", "price": 380.0, "rating": 4.3},
        {"id": "a3", "destination": "Berlin", "price": 320.0, "rating": 4.1},
        {"id": "a4", "destination": "Paris", "price": 350.0, "rating": 4.2},
        {"id": "a5", "destination": "Barcelona", "price": 400.0, "rating": 4.6},
        {"id": "a6", "destination": "Berlin", "price": 290.0, "rating": 3.9},
    ]

    return adapt_trips(raw_trips, MAPPING_A, "ProviderA")