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

        if not is_valid_trip(destination, price, rating):
            continue

        result.append(TripDTO(
            destination=destination,
            price=float(price),
            rating=float(rating),
            provider=provider,
        ))
    return result