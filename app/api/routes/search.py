import uuid
import logging
from datetime import datetime, UTC

from fastapi import APIRouter, Query, Depends

from app.schemas.trip import TripRead
from app.services.search import get_trips_from_providers
from app.services.ranking import rank_trips
from app.services.cache import CacheService
from app.api.deps import get_cache_service, search_rate_limit

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/search", tags=["search"])


@router.get("", response_model=list[TripRead], dependencies=[search_rate_limit])
async def search_trips(
    destination: str = Query(..., min_length=1),
    origin: str = Query(..., min_length=1),
    check_in: str = Query(..., description="ISO date: 2026-05-11"),
    check_out: str = Query(..., description="ISO date: 2026-05-18"),
    max_price: float | None = None,
    hotel_stars: int | None = None,
    mock: bool = Query(True, description="True = mock data, False = RapidAPI real data"),
    cache: CacheService = Depends(get_cache_service),
):
    destination = destination.lower()
    origin = origin.lower()
    max_price = round(max_price, 2) if max_price else None
    stars_filter = hotel_stars if hotel_stars else "none"
    cache_key = f"v1:search:{origin}:{destination}:{check_in}:{check_out}:{max_price if max_price else 'none'}:{stars_filter}:{'mock' if mock else 'real'}"

    cached = await cache.get(cache_key)
    if cached:
        return [TripRead(**item) for item in cached]

    results = await get_trips_from_providers(
        mock=mock,
        origin=origin,
        destination=destination,
        check_in=check_in,
        check_out=check_out,
        hotel_stars=hotel_stars,
    )

    all_trips = []
    for trips in results.values():
        all_trips.extend(trips)

    if mock:
        filtered = [t for t in all_trips if t["destination"].lower() == destination]
    else:
        filtered = list(all_trips)
    if max_price is not None:
        filtered = [t for t in filtered if t["price"] <= max_price]
    if hotel_stars is not None:
        filtered = [t for t in filtered if t.get("hotel_stars") == hotel_stars]

    ranked_trips = rank_trips(filtered, max_price)

    now = datetime.now(UTC)
    response = [
        TripRead(
            id=uuid.uuid4(),
            destination=t["destination"],
            price=t["price"],
            rating=t["rating"],
            provider=t["provider"],
            created_at=now,
            origin=t.get("origin"),
            hotel_stars=t.get("hotel_stars"),
            flight_price=t.get("flight_price"),
            hotel_price=t.get("hotel_price"),
        )
        for t in ranked_trips
    ]

    await cache.set(cache_key, response)

    return response
