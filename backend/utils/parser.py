"""
utils/parser.py — JSON parsing utilities for extracting structured data
from AI model responses that may contain raw JSON or wrapped text.
"""

import json
import logging
import re
from typing import Any

logger = logging.getLogger("agrisense.utils.parser")

# Required top-level fields for a valid diagnosis dict
_REQUIRED_DIAGNOSIS_FIELDS = {
    "disease_name",
    "pathogen",
    "confidence",
    "stage",
    "description",
    "treatment",
    "prevention",
}


def extract_json(text: str) -> dict[str, Any]:
    """
    Robustly extract a JSON object from a string.

    Handles:
    - Pure JSON strings
    - JSON wrapped in markdown code fences (```json ... ```)
    - JSON embedded within explanatory text
    - Trailing commas (common LLM mistake)

    Raises:
        ValueError: If no valid JSON object can be extracted.
    """
    if not text or not text.strip():
        raise ValueError("AI response is empty.")

    # 1. Strip markdown code fences if present
    cleaned = re.sub(r"```(?:json)?\s*", "", text, flags=re.IGNORECASE).strip()
    cleaned = cleaned.rstrip("`").strip()

    # 2. Attempt direct parse
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        pass

    # 3. Find first {...} block in the text
    match = re.search(r"\{.*\}", cleaned, re.DOTALL)
    if match:
        candidate = match.group(0)
        # Fix trailing commas before } or ]
        candidate = re.sub(r",\s*([}\]])", r"\1", candidate)
        try:
            return json.loads(candidate)
        except json.JSONDecodeError as e:
            logger.warning(f"JSON parse failed on extracted block: {e}")

    raise ValueError(
        f"Could not extract valid JSON from AI response. Raw text (first 300 chars): {text[:300]}"
    )


def validate_diagnosis(data: dict[str, Any]) -> dict[str, Any]:
    """
    Validate and sanitize a parsed diagnosis dictionary.

    - Ensures required fields are present with sensible defaults.
    - Clamps confidence to [0, 100].
    - Guarantees list fields are lists.
    - Strips extraneous whitespace.

    Returns the sanitized dictionary.
    """
    # Apply defaults for missing fields
    data.setdefault("disease_name", "Unknown Disease")
    data.setdefault("pathogen", "Unknown Pathogen")
    data.setdefault("confidence", 50)
    data.setdefault("stage", "Unknown")
    data.setdefault("description", "No description provided.")
    data.setdefault("treatment", [])
    data.setdefault("prevention", [])

    # Sanitize confidence
    try:
        data["confidence"] = max(0, min(100, int(data["confidence"])))
    except (TypeError, ValueError):
        data["confidence"] = 50

    # Ensure list fields are actually lists
    for field in ("treatment", "prevention"):
        if not isinstance(data[field], list):
            data[field] = [str(data[field])] if data[field] else []

    # Strip whitespace from string fields
    for field in ("disease_name", "pathogen", "stage", "description"):
        if isinstance(data.get(field), str):
            data[field] = data[field].strip()

    return data
