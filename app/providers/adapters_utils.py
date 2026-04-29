from typing import Any


def is_valid_trip(destination: Any, price: Any, rating: Any) -> bool:
    return (
        destination is not None
        and isinstance(destination, str)
        and price is not None
        and isinstance(price, (int, float))
        and rating is not None
        and isinstance(rating, (int, float))
    )


def _get_nested(data: dict, path: str) -> Any:
    """Get nested value using dot notation."""
    keys = path.split(".")
    value = data
    for key in keys:
        value = value.get(key) if isinstance(value, dict) else None
        if value is None:
            break
    return value