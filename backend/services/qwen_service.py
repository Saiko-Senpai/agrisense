"""
services/qwen_service.py — Qwen Vision Language Model service.

Uses the OpenAI-compatible API endpoint provided by Alibaba DashScope
to send a crop image to Qwen-VL and receive a structured disease diagnosis.
"""

import asyncio
import logging
import os
from typing import Any

import httpx

from utils.parser import extract_json, validate_diagnosis
from utils.prompts import IMAGE_ANALYSIS_PROMPT

logger = logging.getLogger("agrisense.services.qwen")

# Default Qwen DashScope OpenAI-compatible endpoint
QWEN_BASE_URL = os.getenv("QWEN_BASE_URL", "https://dashscope.aliyuncs.com/compatible-mode/v1")
QWEN_MODEL = os.getenv("QWEN_MODEL", "qwen-vl-max")
TIMEOUT_SECONDS = 60


class QwenService:
    """
    Async Qwen Vision model service using the OpenAI-compatible REST API.

    Qwen-VL-Max (DashScope) supports vision inputs via the OpenAI Chat
    Completions format with image_url parts containing base64 data URIs.
    """

    def __init__(self) -> None:
        self._api_key = os.getenv("QWEN_API_KEY")
        if not self._api_key:
            logger.warning("QWEN_API_KEY not set. Qwen service will fail on first call.")

        self._headers = {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json",
        }
        logger.info(f"QwenService initialized with model: {QWEN_MODEL}")

    async def analyze(self, image_base64: str, mime_type: str = "image/jpeg") -> dict[str, Any]:
        """
        Send the image to Qwen Vision and return a structured diagnosis.

        Args:
            image_base64: Base64-encoded image string (no data URI prefix).
            mime_type: Image MIME type (e.g. "image/jpeg").

        Returns:
            Validated diagnosis dictionary.

        Raises:
            RuntimeError: On API error or unparseable response.
        """
        data_uri = f"data:{mime_type};base64,{image_base64}"

        payload = {
            "model": QWEN_MODEL,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image_url",
                            "image_url": {"url": data_uri},
                        },
                        {
                            "type": "text",
                            "text": IMAGE_ANALYSIS_PROMPT,
                        },
                    ],
                }
            ],
            "max_tokens": 1024,
            "temperature": 0.1,
            "response_format": {"type": "json_object"},
        }

        logger.debug("Sending image to Qwen Vision API...")

        try:
            async with httpx.AsyncClient(timeout=TIMEOUT_SECONDS) as client:
                response = await client.post(
                    f"{QWEN_BASE_URL}/chat/completions",
                    headers=self._headers,
                    json=payload,
                )
                response.raise_for_status()
        except httpx.TimeoutException:
            raise RuntimeError(
                f"Qwen API request timed out after {TIMEOUT_SECONDS} seconds."
            )
        except httpx.HTTPStatusError as e:
            raise RuntimeError(
                f"Qwen API returned HTTP {e.response.status_code}: {e.response.text[:200]}"
            ) from e
        except httpx.RequestError as e:
            raise RuntimeError(f"Qwen API network error: {e}") from e

        # Parse the OpenAI-format response
        try:
            data = response.json()
            raw_text = data["choices"][0]["message"]["content"]
        except (KeyError, IndexError, ValueError) as e:
            raise RuntimeError(f"Unexpected Qwen API response structure: {e}") from e

        logger.debug(f"Qwen raw response (first 300 chars): {raw_text[:300]}")

        try:
            parsed = extract_json(raw_text)
            validated = validate_diagnosis(parsed)
        except ValueError as e:
            raise RuntimeError(f"Qwen response parsing failed: {e}") from e

        logger.info(
            f"Qwen diagnosis: {validated['disease_name']} "
            f"({validated['confidence']}% confidence)"
        )
        return validated
