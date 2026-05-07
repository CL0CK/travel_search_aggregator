import asyncio

from app.providers.adapters import adapt_trips, MAPPING_C
from app.schemas.trip import TripDTO


async def provider_c() -> list[TripDTO]:
    """Provider C - Nested API format."""
    await asyncio.sleep(0.8)

    raw_trips = [
        {"meta": {"id": "c1"}, "data": {"destination": "Berlin"}, "pricing": {"amount": 310.0}, "rating": 4.2, "origin": "BER", "hotel_stars": 3, "flight_price": 200.0, "hotel_price": 110.0},
        {"meta": {"id": "c2"}, "data": {"destination": "Barcelona"}, "pricing": {"amount": 390.0}, "rating": 4.4, "origin": "BER", "hotel_stars": 4, "flight_price": 260.0, "hotel_price": 130.0},
        {"meta": {"id": "c3"}, "data": {"destination": "Rome"}, "pricing": {"amount": 440.0}, "rating": 4.6, "origin": "BER", "hotel_stars": 5, "flight_price": 290.0, "hotel_price": 150.0},
        {"meta": {"id": "c4"}, "data": {"destination": "Berlin"}, "pricing": {"amount": 280.0}, "rating": 4.0, "origin": "BER", "hotel_stars": 3, "flight_price": 180.0, "hotel_price": 100.0},
        {"meta": {"id": "c5"}, "data": {"destination": "Barcelona"}, "pricing": {"amount": 370.0}, "rating": 4.7, "origin": "BER", "hotel_stars": 4, "flight_price": 240.0, "hotel_price": 130.0},
        {"meta": {"id": "c6"}, "data": {"destination": "Rome"}, "pricing": {"amount": 460.0}, "rating": 4.3, "origin": "BER", "hotel_stars": 5, "flight_price": 310.0, "hotel_price": 150.0},
    ]

    return adapt_trips(raw_trips, MAPPING_C, "ProviderC")