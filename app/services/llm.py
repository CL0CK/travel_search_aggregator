import logging
import json
import re
import ollama
from pydantic import BaseModel

logger = logging.getLogger(__name__)


class ExtractionResult(BaseModel):
    destination: str | None = None
    origin: str | None = None
    check_in: str | None = None
    check_out: str | None = None
    budget: float | None = None


OLLAMA_MODEL = "phi3:mini"


def _build_prompt(query: str) -> str:
    return (
        f"Extract travel parameters from: {query}. "
        "Return JSON with keys: "
        "destination (city name in English, or null), "
        "origin (departure city in English, or null), "
        "check_in (date in YYYY-MM-DD format, or null), "
        "check_out (date in YYYY-MM-DD format, or null), "
        "budget (number or null). "
        "If a field cannot be determined, use null. "
        "Translate city names to English."
    )


def _parse_response(text: str) -> ExtractionResult:
    text = text.strip()
    json_match = re.search(r'\{[^{}]*\}', text, re.DOTALL)
    if not json_match:
        raise ValueError("Failed to parse LLM response")

    try:
        data = json.loads(json_match.group())
    except json.JSONDecodeError:
        raise ValueError("Failed to parse LLM response")

    dest = data.get("destination")
    origin = data.get("origin")
    check_in = data.get("check_in")
    check_out = data.get("check_out")

    budget = data.get("budget")
    if budget is not None:
        try:
            budget = float(budget)
        except (ValueError, TypeError):
            budget = None

    # Normalize dates — handle "May 11" → "2026-05-11" style if possible
    # For now, trust LLM returns ISO format
    if check_in and not re.match(r'^\d{4}-\d{2}-\d{2}$', str(check_in)):
        check_in = None
    if check_out and not re.match(r'^\d{4}-\d{2}-\d{2}$', str(check_out)):
        check_out = None

    logger.info(
        f"Extracted: dest={dest}, origin={origin}, "
        f"check_in={check_in}, check_out={check_out}, budget={budget}"
    )
    return ExtractionResult(
        destination=dest,
        origin=origin,
        check_in=check_in,
        check_out=check_out,
        budget=budget,
    )


async def extract_travel_params(query: str) -> ExtractionResult:
    prompt = _build_prompt(query)
    response = ollama.chat(
        model=OLLAMA_MODEL,
        messages=[
            {
                "role": "system",
                "content": "You are a travel assistant. Return ONLY valid JSON. No explanations, no text, no markdown.",
            },
            {"role": "user", "content": prompt},
        ],
        options={
            "num_ctx": 2048,
            "num_predict": 256,
            "temperature": 0.0,
        },
    )
    text = response.message.content.strip()
    logger.info(f"LLM response: '{text}'")
    return _parse_response(text)