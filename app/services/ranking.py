from typing import Any


def calculate_score(price: float, rating: float, max_price: float = 1000.0) -> float:
    """Calculate trip score (higher is better)."""
    price_score = 1.0 - min(price / max_price, 1.0)
    rating_score = min(rating / 5.0, 1.0)

    # Equal weights (50/50)
    return 0.5 * price_score + 0.5 * rating_score


def rank_trips(trips: list[dict[str, Any]], max_price: float | None = None) -> list[dict[str, Any]]:
    """Rank trips by score (highest first) and sort before returning."""
    if not trips:
        return []

    reference_max_price = max(t["price"] for t in trips)
    actual_max_price = max_price if max_price else reference_max_price

    for trip in trips:
        trip["score"] = calculate_score(trip["price"], trip["rating"], actual_max_price)

    return sorted(trips, key=lambda x: x["score"], reverse=True)