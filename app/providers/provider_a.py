import asyncio

from app.providers.adapters import adapt_trips, MAPPING_A
from app.schemas.trip import TripDTO


async def provider_a() -> list[TripDTO]:
    """Provider A - Clean API format."""
    await asyncio.sleep(0.3)

    raw_trips = [
        {"id": "a1", "destination": "Paris", "price": 420.0, "rating": 4.5, "origin": "BER", "hotel_stars": 4, "flight_price": 280.0, "hotel_price": 140.0},
        {"id": "a2", "destination": "Barcelona", "price": 380.0, "rating": 4.3, "origin": "BER", "hotel_stars": 4, "flight_price": 250.0, "hotel_price": 130.0},
        {"id": "a3", "destination": "Berlin", "price": 320.0, "rating": 4.1, "origin": "BER", "hotel_stars": 3, "flight_price": 200.0, "hotel_price": 120.0},
        {"id": "a4", "destination": "Paris", "price": 350.0, "rating": 4.2, "origin": "BER", "hotel_stars": 4, "flight_price": 230.0, "hotel_price": 120.0},
        {"id": "a5", "destination": "Barcelona", "price": 400.0, "rating": 4.6, "origin": "BER", "hotel_stars": 5, "flight_price": 260.0, "hotel_price": 140.0},
        {"id": "a6", "destination": "Berlin", "price": 290.0, "rating": 3.9, "origin": "BER", "hotel_stars": 3, "flight_price": 180.0, "hotel_price": 110.0},
    ]

    return adapt_trips(raw_trips, MAPPING_A, "ProviderA")