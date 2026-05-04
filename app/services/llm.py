import logging
import json
import re
import ollama
from pydantic import BaseModel

logger = logging.getLogger(__name__)


class ExtractionResult(BaseModel):
    destination: str
    budget: float | None = None


OLLAMA_MODEL = "phi3:mini"


def _build_prompt(query: str) -> str:
    return (
        f"Extract destination and optional budget from: {query}. "
        "Return JSON with keys destination (string, always in English) and budget (number or null). "
        "If destination is in another language, translate it to English."
    )


def _parse_response(text: str) -> ExtractionResult:
    text = text.strip()
    json_match = re.search(r'\{[^{}]*"destination"[^{}]*\}', text, re.DOTALL)
    if not json_match:
        raise ValueError("Failed to parse LLM response")

    try:
        data = json.loads(json_match.group())
    except json.JSONDecodeError:
        raise ValueError("Failed to parse LLM response")

    dest = data.get("destination")
    if not dest or not isinstance(dest, str):
        raise ValueError("Could not determine destination from query")

    budget = data.get("budget")
    if budget is not None:
        try:
            budget = float(budget)
        except (ValueError, TypeError):
            budget = None

    logger.info(f"Extracted: destination={dest}, budget={budget}")
    return ExtractionResult(destination=dest, budget=budget)


async def extract_travel_params(query: str) -> ExtractionResult:
    prompt = _build_prompt(query)
    response = ollama.chat(
        model=OLLAMA_MODEL,
        messages=[
            {
                "role": "system",
                "content": "You are a travel assistant. Return ONLY valid JSON. No explanations, no text, no markdown."
             },
            {"role": "user", "content": prompt},
        ],
        options={
            "num_ctx": 2048,
            "num_predict": 128,
            "temperature": 0.0,
        },
    )
    text = response.message.content.strip()
    logger.info(f"LLM response: '{text}'")
    return _parse_response(text)