import asyncio

from app.providers.adapters import adapt_trips, MAPPING_C
from app.schemas.trip import TripDTO


async def provider_c() -> list[TripDTO]:
    """Provider C - Nested API format."""
    await asyncio.sleep(0.8)

    raw_trips = [
        {"meta": {"id": "c1"}, "data": {"destination": "Berlin"}, "pricing": {"amount": 310.0}, "rating": 4.2},
        {"meta": {"id": "c2"}, "data": {"destination": "Barcelona"}, "pricing": {"amount": 390.0}, "rating": 4.4},
        {"meta": {"id": "c3"}, "data": {"destination": "Rome"}, "pricing": {"amount": 440.0}, "rating": 4.6},
    ]

    return adapt_trips(raw_trips, MAPPING_C, "ProviderC")