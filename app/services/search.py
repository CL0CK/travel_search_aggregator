import asyncio
from typing import Any

from app.providers import provider_a, provider_b, provider_c


async def search_providers() -> dict[str, list[dict[str, Any]]]:
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