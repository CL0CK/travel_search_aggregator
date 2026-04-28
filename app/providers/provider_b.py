import asyncio
from typing import Any


async def provider_b() -> list[dict[str, Any]]:
    """Provider B - Messy legacy API format."""
    await asyncio.sleep(1.5)
    
    return [
        {"trip_id": "b1", "city": "Rome", "cost": 450.0, "stars": 4.7},
        {"trip_id": "b2", "city": "London", "cost": 520.0, "stars": 4.6},
        {"trip_id": "b3", "city": "Paris", "cost": 410.0, "stars": 4.4},
    ]