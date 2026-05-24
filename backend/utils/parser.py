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


def parse_markdown_fallback(text: str) -> dict[str, Any]:
    """
    Fallback parser when LLM outputs markdown or key-value format instead of JSON.
    """
    result = {}
    
    # Disease Name
    disease_match = re.search(r"(?:disease\s*name|disease)\s*:\s*\**([^\n\*\r]+)", text, re.IGNORECASE)
    if disease_match:
        result["disease_name"] = disease_match.group(1).strip("* ").strip()
        
    # Pathogen
    pathogen_match = re.search(r"(?:pathogen)\s*:\s*\**([^\n\*\r]+)", text, re.IGNORECASE)
    if pathogen_match:
        result["pathogen"] = pathogen_match.group(1).strip("* ").strip()
        
    # Confidence
    confidence_match = re.search(r"(?:confidence)\s*:\s*\**(\d+)", text, re.IGNORECASE)
    if confidence_match:
        result["confidence"] = int(confidence_match.group(1))
        
    # Stage
    stage_match = re.search(r"(?:stage)\s*:\s*\**([^\n\*\r]+)", text, re.IGNORECASE)
    if stage_match:
        result["stage"] = stage_match.group(1).strip("* ").strip()
        
    # Description
    desc_match = re.search(r"(?:description)\s*:\s*\**([^\n\r]+)", text, re.IGNORECASE)
    if desc_match:
        result["description"] = desc_match.group(1).strip("* ").strip()

    # Now extract lists for treatment and prevention
    for field in ("treatment", "prevention"):
        items = []
        block_pattern = rf"(?:{field}|{field}s)\s*:\s*(.*?)(?=(?:\n\s*\*?\*?\w+\s*:\s*)|$)"
        block_match = re.search(block_pattern, text, re.IGNORECASE | re.DOTALL)
        if block_match:
            block_text = block_match.group(1)
            bullets = re.findall(r"(?:^|\n)\s*(?:\*|-|\d+\.)\s*(.*?)(?=\n\s*(?:\*|-|\d+\.)|$)", block_text)
            for bullet in bullets:
                b_cleaned = bullet.strip("* ").strip()
                if b_cleaned:
                    items.append(b_cleaned)
            if not items:
                lines = [line.strip() for line in block_text.split("\n") if line.strip()]
                for line in lines:
                    cleaned_line = line.strip("*- \t0123456789.")
                    if cleaned_line:
                        items.append(cleaned_line)
        result[field] = items

    return result


def extract_json(text: str) -> dict[str, Any]:
    """
    Robustly extract a JSON object from a string.

    Handles:
    - Pure JSON strings
    - JSON wrapped in markdown code fences (```json ... ```)
    - JSON embedded within explanatory text
    - Trailing commas (common LLM mistake)
    - Markdown key-value fallback parser (if JSON parsing completely fails)

    Raises:
        ValueError: If no valid JSON or structured metadata can be parsed.
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

    # 4. Fallback: Parse markdown key-value pairs
    try:
        parsed_md = parse_markdown_fallback(text)
        # Verify that we extracted at least the disease name
        if parsed_md.get("disease_name"):
            logger.info("Successfully recovered structured disease data using markdown fallback parser.")
            return parsed_md
    except Exception as e:
        logger.warning(f"Markdown fallback parsing failed: {e}")

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
