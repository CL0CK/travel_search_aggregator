import asyncio
from typing import Any


async def provider_c() -> list[dict[str, Any]]:
    """Provider C - Nested API format."""
    await asyncio.sleep(0.8)
    
    return [
        {"meta": {"id": "c1"}, "data": {"destination": "Berlin"}, "pricing": {"amount": 310.0}, "rating": 4.2},
        {"meta": {"id": "c2"}, "data": {"destination": "Barcelona"}, "pricing": {"amount": 390.0}, "rating": 4.4},
        {"meta": {"id": "c3"}, "data": {"destination": "Rome"}, "pricing": {"amount": 440.0}, "rating": 4.6},
    ]