import asyncio

from app.providers import provider_a, provider_b, provider_c, provider_rapidapi
from app.schemas.trip import TripDTO


async def get_trips_from_providers(
    mock: bool = True,
    origin: str = "",
    destination: str = "",
    check_in: str = "",
    check_out: str = "",
    hotel_stars: int | None = None,
) -> dict[str, list[TripDTO]]:
    """Call providers in parallel. mock=True uses mock providers, mock=False uses RapidAPI."""
    if mock:
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
    else:
        results = await provider_rapidapi(
            origin=origin,
            destination=destination,
            check_in=check_in,
            check_out=check_out,
            hotel_stars=hotel_stars,
        )
        return {
            "rapidapi": results,
        }