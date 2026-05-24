"""
services/gemini_service.py — Gemini Vision model service.

Sends a preprocessed crop image to the Google Gemini Vision API
and returns a structured disease diagnosis dictionary.
"""

import asyncio
import logging
import os
from typing import Any

import google.generativeai as genai

from utils.parser import extract_json, validate_diagnosis
from utils.prompts import IMAGE_ANALYSIS_PROMPT

logger = logging.getLogger("agrisense.services.gemini")


class GeminiService:
    """
    Async wrapper around the Google Gemini Generative AI SDK.

    Uses the gemini-1.5-flash model by default for fast, cost-effective
    vision analysis. Switch to gemini-1.5-pro for higher accuracy.
    """

    def __init__(self) -> None:
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            logger.warning("GEMINI_API_KEY not set. Gemini service will fail on first call.")
        else:
            genai.configure(api_key=api_key)

        model_name = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
        self._model = genai.GenerativeModel(
            model_name=model_name,
            generation_config=genai.GenerationConfig(
                temperature=0.1,       # Low temperature for deterministic, factual output
                max_output_tokens=1024,
                response_mime_type="application/json",  # Enforce JSON output natively
            ),
        )
        logger.info(f"GeminiService initialized with model: {model_name}")

    async def analyze(self, image_base64: str, mime_type: str = "image/jpeg") -> dict[str, Any]:
        """
        Send the image to Gemini Vision and return a structured diagnosis.

        Args:
            image_base64: Base64-encoded image string (no data URI prefix).
            mime_type: Image MIME type (e.g. "image/jpeg").

        Returns:
            Validated diagnosis dictionary with keys:
            disease_name, pathogen, confidence, stage, description,
            treatment, prevention.

        Raises:
            RuntimeError: On API call failure or unparseable response.
        """
        logger.debug("Sending image to Gemini Vision API...")

        # Construct the multimodal content parts
        image_part = {"mime_type": mime_type, "data": image_base64}
        content = [IMAGE_ANALYSIS_PROMPT, image_part]

        try:
            # Gemini SDK is synchronous — run in a thread pool to keep the event loop free
            response = await asyncio.get_event_loop().run_in_executor(
                None, lambda: self._model.generate_content(content)
            )
        except Exception as e:
            logger.error(f"Gemini API call failed: {e}", exc_info=True)
            raise RuntimeError(f"Gemini Vision API error: {e}") from e

        # Extract and validate the response text
        raw_text = ""
        try:
            raw_text = response.text
        except Exception as e:
            raise RuntimeError(f"Gemini returned an empty or blocked response: {e}") from e

        logger.debug(f"Gemini raw response (first 300 chars): {raw_text[:300]}")

        try:
            parsed = extract_json(raw_text)
            validated = validate_diagnosis(parsed)
        except ValueError as e:
            raise RuntimeError(f"Gemini response parsing failed: {e}") from e

        logger.info(
            f"Gemini diagnosis: {validated['disease_name']} "
            f"({validated['confidence']}% confidence)"
        )
        return validated
