import logging

from fastapi import APIRouter, HTTPException, status

from app.services.llm import extract_travel_params

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/extract", tags=["extract"])


@router.post("")
async def extract(body: dict):
    query = body.get("query", "")
    if not query:
        raise HTTPException(status_code=400, detail="Query is empty")
    accumulated = body.get("accumulated")
    try:
        result = await extract_travel_params(query, accumulated)
        if not result.valid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Your query doesn't seem to be about travel. Please describe your trip with destination, origin, and dates.",
            )
        return result.model_dump()
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"LLM extraction failed for query '{query[:50]}': {e}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Failed to extract travel parameters from your query. Please try rephrasing.",
        )
