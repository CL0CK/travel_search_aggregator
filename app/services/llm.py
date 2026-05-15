import logging
import json
import re
from datetime import datetime

import ollama
from pydantic import BaseModel

from app.providers.provider_rapidapi import FLIGHT_CODES

logger = logging.getLogger(__name__)


class ExtractionResult(BaseModel):
    destination: str | None = None
    origin: str | None = None
    check_in: str | None = None
    check_out: str | None = None
    budget: float | None = None
    valid: bool = True


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


def _normalize_city_name(name: str | None) -> str | None:
    if not name:
        return None
    cleaned = name.lower().strip()
    code = FLIGHT_CODES.get(cleaned)
    if code:
        # Find English version: another key that maps to same code and is ASCII
        for cn, c in FLIGHT_CODES.items():
            if c == code and cn.isascii():
                return cn.title()
        return cleaned.title()
    return name.strip()


def _build_prompt(cleaned_query: str, accumulated: dict | None = None) -> str:
    parts = [f"Extract travel parameters from: {cleaned_query}."]
    if accumulated:
        known = []
        if accumulated.get("destination"):
            known.append(f"destination = {accumulated['destination']}")
        if accumulated.get("origin"):
            known.append(f"origin = {accumulated['origin']}")
        if known:
            parts.append(f"We already know: {', '.join(known)}.")
    parts.append(
        "Return ONLY valid JSON with keys: "
        "valid (false if NOT about travel/hotels/vacation, else true), "
        "destination (city name, or null), "
        "origin (departure city, or null), "
        "budget (number or null). "
        "Do NOT extract dates. Use null for missing fields. "
        "NEVER invent cities. Pay attention to direction words: "
        "'from/von/aus/из' indicates origin, 'to/nach/in/в' indicates destination. "
        "Return ONLY valid JSON."
    )
    return " ".join(parts)


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


def _city_in_query(city: str, query: str) -> bool:
    """Check if a city name (in any language) appears in the original query."""
    q = query.lower()
    if city.lower() in q:
        return True
    code = FLIGHT_CODES.get(city.lower().strip())
    if code:
        for cn, c in FLIGHT_CODES.items():
            if c == code and cn in q:
                return True
    return False


def _is_hallucination(dest: str | None, origin: str | None, query: str) -> bool:
    if not dest and not origin:
        return False
    for city in (dest, origin):
        if city and not _city_in_query(city, query):
            return True
    return False


async def extract_travel_params(query: str, accumulated: dict | None = None) -> ExtractionResult:
    check_in, check_out, cleaned = _extract_dates_from_query(query)

    dest = origin = None
    budget = None
    llm_called = False

    if _has_meaningful_words(cleaned):
        llm_called = True
        prompt = _build_prompt(cleaned, accumulated)
        try:
            response = ollama.chat(
                model=OLLAMA_MODEL,
                messages=[
                    {
                        "role": "system",
                        "content": "You extract travel data. Return JSON only.",
                    },
                    {"role": "user", "content": prompt},
                ],
                options={
                    "num_ctx": 2048,
                    "num_predict": 256,
                    "temperature": 0.0,
                },
                format="json",
            )
            text = response.message.content.strip()
            logger.info(f"LLM response (cleaned '{cleaned[:60]}'): '{text[:200]}'")

            data = _parse_llm_json(text)
            if data.get("valid") is False:
                return ExtractionResult(valid=False)
            dest = _normalize_city_name(data.get("destination"))
            origin = _normalize_city_name(data.get("origin"))
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

    if llm_called:
        if dest and not _city_in_query(dest, cleaned):
            logger.info(f"Hallucinated destination '{dest}' removed")
            dest = None
        if origin and not _city_in_query(origin, cleaned):
            logger.info(f"Hallucinated origin '{origin}' removed")
            origin = None
        if dest and origin and dest.lower() == origin.lower():
            q = cleaned.lower()
            has_from = any(m in q for m in ["from ", "von ", "из "])
            has_to = any(m in q for m in [" to ", " nach ", " в ", "to "])
            if has_from and not has_to:
                dest = None
            elif has_to and not has_from:
                origin = None
        if not dest and not origin and not check_in and not check_out:
            logger.info(f"All fields hallucinated, marking invalid")
            return ExtractionResult(valid=False)

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
