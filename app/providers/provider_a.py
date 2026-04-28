import asyncio
from typing import Any


async def provider_a() -> list[dict[str, Any]]:
    """Provider A - Clean API format."""
    await asyncio.sleep(0.3)
    
    return [
        {"id": "a1", "destination": "Paris", "price": 420.0, "rating": 4.5},
        {"id": "a2", "destination": "Barcelona", "price": 380.0, "rating": 4.3},
        {"id": "a3", "destination": "Berlin", "price": 320.0, "rating": 4.1},
    ]