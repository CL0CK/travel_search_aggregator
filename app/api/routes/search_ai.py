import uuid
import logging
from datetime import datetime, UTC

from fastapi import APIRouter, Depends, HTTPException, status

from app.schemas.trip import TripRead
from app.schemas.search_ai import SearchAIRequest, SearchAIResponse
from app.services.search import get_trips_from_providers
from app.services.ranking import rank_trips
from app.services.llm import extract_travel_params
from app.services.cache import CacheService
from app.api.deps import get_cache_service, search_ai_rate_limit
from app.providers.provider_rapidapi import FLIGHT_CODES as _RAPID_FLIGHT_CODES


def _airport_code(city: str) -> str | None:
    code = _RAPID_FLIGHT_CODES.get(city.lower().strip())
    if code:
        return code.replace(".AIRPORT", "")
    return None

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/search_ai", tags=["ai"])


@router.post("", response_model=SearchAIResponse, dependencies=[search_ai_rate_limit])
async def search_trips_ai(
    body: SearchAIRequest,
    cache: CacheService = Depends(get_cache_service),
):
    try:
        extracted = await extract_travel_params(body.query)
    except Exception as e:
        logger.error(f"LLM extraction failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process query with AI",
        )

    if not extracted.valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Your query doesn't seem to be about travel. Please describe your trip with destination, origin, and dates.",
        )
    if not extracted.destination:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not determine destination. Please specify a city.",
        )
    if not extracted.origin:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Please specify your departure city.",
        )
    if not extracted.check_in or not extracted.check_out:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Please specify your travel dates.",
        )

    destination = extracted.destination.lower()
    origin = extracted.origin.lower()
    budget = round(extracted.budget, 2) if extracted.budget else None
    check_in = extracted.check_in
    check_out = extracted.check_out
    cache_key = f"v1:search_ai:{origin}:{destination}:{check_in}:{check_out}:{budget if budget else 'none'}:{'mock' if body.mock else 'real'}"

    cached = await cache.get(cache_key)
    if cached:
        return SearchAIResponse(**cached)

    results = await get_trips_from_providers(
        mock=body.mock,
        origin=origin,
        destination=destination,
        check_in=check_in,
        check_out=check_out,
        hotel_stars=None,
    )
    all_trips = []
    for trips in results.values():
        all_trips.extend(trips)

    filtered = list(all_trips) if not body.mock else [t for t in all_trips if t["destination"].lower() == destination]
    if budget is not None:
        filtered = [t for t in filtered if t["price"] <= budget]

    ranked = rank_trips(filtered, budget)

    from_code = _airport_code(origin)
    to_code = _airport_code(destination)
    now = datetime.now(UTC)
    response_data = SearchAIResponse(
        destination=destination,
        origin=origin,
        budget=budget,
        results=[
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
                check_in=check_in,
                check_out=check_out,
                from_airport=from_code,
                to_airport=to_code,
                booking_url=t.get("booking_url"),
            )
            for t in ranked
        ],
    )

    await cache.set(cache_key, response_data)
    return response_data
