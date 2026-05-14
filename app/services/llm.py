import logging
import json
import re
from datetime import datetime

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

_DATE_PATTERNS = [
    (r'(\d{4})-(\d{2})-(\d{2})', lambda m: f"{m[1]}-{m[2]}-{m[3]}"),
    (r'(\d{2})\.(\d{2})\.(\d{4})', lambda m: f"{m[3]}-{m[2]}-{m[1]}"),
    (r'(\d{2})/(\d{2})/(\d{4})', lambda m: f"{m[3]}-{m[2]}-{m[1]}"),
]


def _extract_dates_from_query(query: str) -> tuple[str | None, str | None, str]:
    """Extract up to 2 dates from query, return (check_in, check_out, cleaned_query)."""
    found = []
    cleaned = query

    for pattern, formatter in _DATE_PATTERNS:
        for m in re.finditer(pattern, query):
            raw = m.group(0)
            normalized = formatter(m)
            try:
                datetime.strptime(normalized, "%Y-%m-%d")
                found.append((normalized, raw))
            except ValueError:
                pass

    # Remove matched date strings from query (longest first to avoid offset issues)
    for _, raw in sorted(found, key=lambda x: -len(x[1])):
        cleaned = cleaned.replace(raw, "").strip()

    if not found:
        return None, None, cleaned

    found.sort(key=lambda x: x[0])
    check_in = found[0][0]
    check_out = found[-1][0] if len(found) >= 2 else None

    return check_in, check_out, cleaned


def _build_prompt(cleaned_query: str) -> str:
    return (
        f"Extract travel parameters from: {cleaned_query}. "
        "Return ONLY valid JSON with keys: "
        "destination (city name in English, or null), "
        "origin (departure city in English, or null), "
        "budget (number or null). "
        "Do NOT extract dates. Do NOT add explanations. "
        "If a field cannot be determined, use null. "
        "Translate city names to English."
    )


def _strip_markdown(text: str) -> str:
    text = re.sub(r'^```(?:json)?\s*', '', text, flags=re.MULTILINE)
    text = re.sub(r'\s*```$', '', text, flags=re.MULTILINE)
    return text.strip()


def _parse_llm_json(text: str) -> dict:
    text = _strip_markdown(text)
    json_match = re.search(r'\{[^{}]*\}', text, re.DOTALL)
    if not json_match:
        raise ValueError("Failed to parse LLM response")
    try:
        return json.loads(json_match.group())
    except json.JSONDecodeError:
        raise ValueError("Failed to parse LLM response")


_STOP_WORDS = frozenset({"", "a", "an", "the", "to", "from", "in", "at", "and", "or", "of", "for", "i", "me", "my", "we", "our", "want", "go", "going", "need", "like", "would", "please", "travel", "trip", "flight", "book", "looking"})


def _has_meaningful_words(text: str) -> bool:
    words = text.lower().split()
    return any(w not in _STOP_WORDS and w.isalpha() and len(w) > 1 for w in words)


async def extract_travel_params(query: str) -> ExtractionResult:
    check_in, check_out, cleaned = _extract_dates_from_query(query)

    dest = origin = None
    budget = None

    if _has_meaningful_words(cleaned):
        prompt = _build_prompt(cleaned)
        try:
            response = ollama.chat(
                model=OLLAMA_MODEL,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a travel assistant. Return ONLY valid JSON. No explanations.",
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
            logger.info(f"LLM response (cleaned '{cleaned[:60]}'): '{text[:200]}'")

            data = _parse_llm_json(text)
            dest = data.get("destination")
            origin = data.get("origin")
            raw_budget = data.get("budget")
            if raw_budget is not None:
                try:
                    budget = float(raw_budget)
                except (ValueError, TypeError):
                    budget = None
        except Exception as e:
            logger.warning(f"LLM extraction failed for cleaned query '{cleaned[:50]}': {e}")
            # Return partial result with dates only
    else:
        logger.info(f"Skipping LLM: cleaned query has no meaningful content: '{cleaned[:60]}'")

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
