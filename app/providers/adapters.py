from typing import Any

from app.providers.adapters_utils import is_valid_trip, _get_nested
from app.schemas.trip import TripDTO


MAPPING_A = {"destination": "destination", "price": "price", "rating": "rating"}
MAPPING_B = {"destination": "city", "price": "cost", "rating": "stars"}
MAPPING_C = {"destination": "data.destination", "price": "pricing.amount", "rating": "rating"}


def adapt_trips(
    trips: list[dict[str, Any]],
    mapping: dict[str, str],
    provider: str,
) -> list[TripDTO]:
    """Generic adapter using field mapping."""
    result = []
    for trip in trips:
        destination = _get_nested(trip, mapping["destination"])
        price = _get_nested(trip, mapping["price"])
        rating = _get_nested(trip, mapping["rating"])
        origin = trip.get("origin")
        hotel_stars = trip.get("hotel_stars")
        flight_price = trip.get("flight_price")
        hotel_price = trip.get("hotel_price")

        if not is_valid_trip(destination, price, rating):
            continue

        dto: TripDTO = {
            "destination": destination,
            "price": float(price),
            "rating": float(rating),
            "provider": provider,
        }
        if origin:
            dto["origin"] = origin
        if hotel_stars is not None:
            dto["hotel_stars"] = int(hotel_stars)
        if flight_price is not None:
            dto["flight_price"] = float(flight_price)
        if hotel_price is not None:
            dto["hotel_price"] = float(hotel_price)

        result.append(dto)
    return result