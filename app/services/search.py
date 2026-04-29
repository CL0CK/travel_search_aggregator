import asyncio

from app.providers import provider_a, provider_b, provider_c
from app.schemas.trip import TripDTO


async def get_trips_from_providers() -> dict[str, list[TripDTO]]:
    """Call all providers in parallel."""
    results_a, results_b, results_c = await asyncio.gather(
        provider_a(),
        provider_b(),
        provider_c(),
    )
    
    return {
        "provider_a": results_a,
        "provider_b": results_b,
        "provider_c": results_c,
    }