"""
services/llama_service.py — Llama Vision model service on OpenRouter.

Sends a preprocessed crop image to the Meta Llama 3.2 Vision API via OpenRouter
and returns a structured disease diagnosis dictionary.
"""

import asyncio
import logging
import os
from typing import Any

import httpx

from utils.parser import extract_json, validate_diagnosis
from utils.prompts import IMAGE_ANALYSIS_PROMPT

logger = logging.getLogger("agrisense.services.llama")

OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
LLAMA_MODEL = os.getenv("LLAMA_MODEL", "meta-llama/llama-3.2-11b-vision-instruct")
TIMEOUT_SECONDS = 60


class LlamaService:
    """
    Async Llama Vision model service using OpenRouter's OpenAI-compatible REST API.
    """

    def __init__(self) -> None:
        # Fall back to QWEN_API_KEY if LLAMA_API_KEY is not defined, since they are both OpenRouter keys
        self._api_key = os.getenv("LLAMA_API_KEY") or os.getenv("QWEN_API_KEY")
        if not self._api_key:
            logger.warning("LLAMA_API_KEY / QWEN_API_KEY not set. Llama service will fail.")

        self._headers = {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://agrisense.ai",
            "X-Title": "AgriSense AI",
        }
        logger.info(f"LlamaService initialized with model: {LLAMA_MODEL}")

    async def analyze(self, image_base64: str, mime_type: str = "image/jpeg") -> dict[str, Any]:
        """
        Send the image to Llama Vision and return a structured diagnosis.
        """
        logger.debug("Sending image to Llama Vision API via OpenRouter...")
        data_uri = f"data:{mime_type};base64,{image_base64}"

        payload = {
            "model": LLAMA_MODEL,
            "messages": [
                {
                    "role": "system",
                    "content": "You are a professional agricultural pathologist. You must respond ONLY with a single valid JSON object matching the requested schema. Do not output any markdown headers, bold titles, bullet points, introductory remarks, or code blocks outside the JSON."
                },
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

        try:
            async with httpx.AsyncClient(timeout=TIMEOUT_SECONDS) as client:
                response = await client.post(
                    f"{OPENROUTER_BASE_URL}/chat/completions",
                    headers=self._headers,
                    json=payload,
                )
                response.raise_for_status()
        except httpx.TimeoutException:
            raise RuntimeError(
                f"Llama API request timed out after {TIMEOUT_SECONDS} seconds."
            )
        except httpx.HTTPStatusError as e:
            raise RuntimeError(
                f"Llama API returned HTTP {e.response.status_code}: {e.response.text[:200]}"
            ) from e
        except httpx.RequestError as e:
            raise RuntimeError(f"Llama API network error: {e}") from e

        # Parse response
        try:
            data = response.json()
            raw_text = data["choices"][0]["message"]["content"]
        except (KeyError, IndexError, ValueError) as e:
            raise RuntimeError(f"Unexpected Llama API response structure: {e}") from e

        logger.debug(f"Llama raw response (first 300 chars): {raw_text[:300]}")

        try:
            parsed = extract_json(raw_text)
            validated = validate_diagnosis(parsed)
        except ValueError as e:
            raise RuntimeError(f"Llama response parsing failed: {e}") from e

        logger.info(
            f"Llama diagnosis: {validated['disease_name']} "
            f"({validated['confidence']}% confidence)"
        )
        return validated
