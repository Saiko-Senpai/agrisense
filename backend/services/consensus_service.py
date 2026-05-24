"""
services/consensus_service.py — External Research API consensus service.

Triggered ONLY when Gemini (primary) and Qwen (secondary) disagree
on the disease diagnosis.

The consensus service calls an external, research-backed plant disease
database/API to obtain an authoritative, scientifically validated result.

Configuration (via .env):
    CONSENSUS_API_URL   — The base URL of the research API endpoint
    CONSENSUS_API_KEY   — Bearer token / API key for authentication

The external API is expected to receive a POST request with:
    {
        "gemini_diagnosis": { ...structured diagnosis dict... },
        "qwen_diagnosis":   { ...structured diagnosis dict... }
    }

And return a JSON response with the validated diagnosis fields:
    {
        "disease_name": "...",
        "pathogen": "...",
        "confidence": 0-100,
        "stage": "...",
        "description": "...",
        "treatment": [...],
        "prevention": [...]
    }

If the external API does not match this schema exactly, the response
is passed through the standard parser/validator for normalization.
"""

import logging
import os
from typing import Any

import httpx

from utils.parser import extract_json, validate_diagnosis

logger = logging.getLogger("agrisense.services.consensus")

TIMEOUT_SECONDS = 30


class ConsensusService:
    """
    Calls an external plant disease research API to arbitrate between
    conflicting Gemini and Qwen diagnoses.

    The external API acts as a scientific ground-truth source, providing
    research-validated disease identification results.
    """

    def __init__(self) -> None:
        self._api_url = os.getenv("CONSENSUS_API_URL", "").rstrip("/")
        self._api_key = os.getenv("CONSENSUS_API_KEY", "")

        if not self._api_url:
            logger.warning(
                "CONSENSUS_API_URL is not set. "
                "Consensus service will raise RuntimeError on first call. "
                "Set CONSENSUS_API_URL in your .env file."
            )
        else:
            logger.info(f"ConsensusService initialized → endpoint: {self._api_url}")

    async def arbitrate(
        self,
        gemini_result: dict[str, Any],
        qwen_result: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Submit both VLM diagnoses to the research API for consensus validation.

        Args:
            gemini_result: Structured diagnosis dict from GeminiService (primary).
            qwen_result: Structured diagnosis dict from QwenService (secondary).

        Returns:
            A validated, sanitized diagnosis dictionary tagged with source="consensus".

        Raises:
            RuntimeError: If the API is unreachable, returns a non-200 status,
                          or returns an unparseable response.
        """
        if not self._api_url:
            raise RuntimeError(
                "Consensus API URL is not configured. "
                "Please set CONSENSUS_API_URL in your .env file."
            )

        logger.info(
            f"Consensus arbitration → "
            f"Gemini said: '{gemini_result.get('disease_name')}' | "
            f"Qwen said: '{qwen_result.get('disease_name')}'"
        )

        # Build the request payload
        payload = self._build_payload(gemini_result, qwen_result)

        # Build request headers
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        if self._api_key:
            headers["Authorization"] = f"Bearer {self._api_key}"

        # Call the research API
        try:
            async with httpx.AsyncClient(timeout=TIMEOUT_SECONDS) as client:
                response = await client.post(
                    self._api_url,
                    json=payload,
                    headers=headers,
                )
                response.raise_for_status()

        except httpx.TimeoutException:
            raise RuntimeError(
                f"Consensus research API timed out after {TIMEOUT_SECONDS}s. "
                f"Endpoint: {self._api_url}"
            )
        except httpx.HTTPStatusError as e:
            raise RuntimeError(
                f"Consensus API returned HTTP {e.response.status_code}: "
                f"{e.response.text[:300]}"
            ) from e
        except httpx.RequestError as e:
            raise RuntimeError(
                f"Consensus API network error: {e}. "
                f"Check that CONSENSUS_API_URL is reachable."
            ) from e

        # Parse and normalize the response
        try:
            raw = response.json()
        except Exception:
            raw_text = response.text
            logger.debug(f"Consensus raw text response: {raw_text[:400]}")
            try:
                raw = extract_json(raw_text)
            except ValueError as e:
                raise RuntimeError(
                    f"Consensus API returned non-JSON response: {e}"
                ) from e

        # The research API may wrap its result — unwrap common envelope patterns
        result_data = self._unwrap(raw)

        # Validate and sanitize against our schema
        try:
            validated = validate_diagnosis(result_data)
        except Exception as e:
            raise RuntimeError(
                f"Consensus API response failed schema validation: {e}"
            ) from e

        validated["source"] = "consensus"

        logger.info(
            f"Consensus result: '{validated['disease_name']}' "
            f"({validated['confidence']}% confidence)"
        )
        return validated

    # -----------------------------------------------------------------------
    # Helpers
    # -----------------------------------------------------------------------

    def _build_payload(
        self,
        gemini_result: dict[str, Any],
        qwen_result: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Build the POST payload for the research consensus API.

        Sends both VLM diagnoses so the research API has full context
        to make an informed arbitration decision.
        """
        return {
            "primary_diagnosis": {
                "model": "gemini",
                "disease_name": gemini_result.get("disease_name", ""),
                "pathogen": gemini_result.get("pathogen", ""),
                "confidence": gemini_result.get("confidence", 0),
                "stage": gemini_result.get("stage", ""),
                "description": gemini_result.get("description", ""),
                "treatment": gemini_result.get("treatment", []),
                "prevention": gemini_result.get("prevention", []),
            },
            "secondary_diagnosis": {
                "model": "qwen",
                "disease_name": qwen_result.get("disease_name", ""),
                "pathogen": qwen_result.get("pathogen", ""),
                "confidence": qwen_result.get("confidence", 0),
                "stage": qwen_result.get("stage", ""),
                "description": qwen_result.get("description", ""),
                "treatment": qwen_result.get("treatment", []),
                "prevention": qwen_result.get("prevention", []),
            },
        }

    def _unwrap(self, raw: dict[str, Any]) -> dict[str, Any]:
        """
        Unwrap common API response envelope patterns.

        Many research APIs wrap their result in a top-level key like:
            { "data": { ...diagnosis... } }
            { "result": { ...diagnosis... } }
            { "diagnosis": { ...diagnosis... } }

        If no known wrapper is found, assume the raw dict IS the diagnosis.
        """
        for key in ("data", "result", "diagnosis", "response"):
            if key in raw and isinstance(raw[key], dict):
                logger.debug(f"Unwrapped consensus response from '{key}' key.")
                return raw[key]
        return raw
