import asyncio

from app.providers.adapters import adapt_trips, MAPPING_B
from app.schemas.trip import TripDTO


async def provider_b() -> list[TripDTO]:
    """Provider B - Messy legacy API format."""
    await asyncio.sleep(1.5)

    raw_trips = [
        {"trip_id": "b1", "city": "Rome", "cost": 450.0, "stars": 4.7, "origin": "BER", "hotel_stars": 5, "flight_price": 300.0, "hotel_price": 150.0},
        {"trip_id": "b2", "city": "London", "cost": 520.0, "stars": 4.6, "origin": "BER", "hotel_stars": 5, "flight_price": 340.0, "hotel_price": 180.0},
        {"trip_id": "b3", "city": "Paris", "cost": 410.0, "stars": 4.4, "origin": "BER", "hotel_stars": 4, "flight_price": 270.0, "hotel_price": 140.0},
        {"trip_id": "b4", "city": "Rome", "cost": 380.0, "stars": 4.2, "origin": "BER", "hotel_stars": 4, "flight_price": 250.0, "hotel_price": 130.0},
        {"trip_id": "b5", "city": "London", "cost": 490.0, "stars": 4.8, "origin": "BER", "hotel_stars": 5, "flight_price": 320.0, "hotel_price": 170.0},
        {"trip_id": "b6", "city": "Paris", "cost": 390.0, "stars": 4.6, "origin": "BER", "hotel_stars": 4, "flight_price": 260.0, "hotel_price": 130.0},
    ]

    return adapt_trips(raw_trips, MAPPING_B, "ProviderB")