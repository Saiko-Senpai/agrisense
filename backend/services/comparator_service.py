"""
services/comparator_service.py — Llama-powered diagnosis comparison service via OpenRouter.

Uses the OpenRouter API to determine whether the Llama (primary) and Qwen (secondary)
VLM diagnoses refer to the same disease.
"""

import asyncio
import logging
import os
import httpx
from typing import Any

from utils.parser import extract_json
from utils.prompts import build_comparison_prompt

logger = logging.getLogger("agrisense.services.comparator")


class ComparatorService:
    """
    Llama/Qwen-powered intelligent diagnosis comparator.
    """

    def __init__(self) -> None:
        self._api_key = os.getenv("QWEN_API_KEY")
        if not self._api_key:
            logger.warning("QWEN_API_KEY not set. Comparator will fail on first call.")
        logger.info("ComparatorService initialized with OpenRouter comparison engine.")

    async def compare(
        self,
        llama_result: dict[str, Any],
        qwen_result: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Ask OpenRouter to determine whether both VLM outputs describe the same disease.
        """
        llama_disease = llama_result.get("disease_name", "Unknown")
        if "disease" in llama_result:
            llama_disease = llama_result.get("disease", "Unknown")
            
        qwen_disease = qwen_result.get("disease_name", "Unknown")
        if "disease" in qwen_result:
            qwen_disease = qwen_result.get("disease", "Unknown")

        logger.info(
            f"Comparator | Primary (Llama): '{llama_disease}' vs "
            f"Secondary (Qwen): '{qwen_disease}'"
        )

        # --- Quick shortcut: if both say "Healthy Plant", they trivially agree ---
        if (
            "healthy" in llama_disease.lower()
            and "healthy" in qwen_disease.lower()
        ):
            logger.info("Comparator | Both models agree: Healthy Plant (shortcut match)")
            return {
                "matched": True,
                "reasoning": "Both models independently identified the plant as healthy.",
                "confidence": 100,
                "llama_disease": llama_disease,
                "qwen_disease": qwen_disease,
            }

        # --- Build and send comparison prompt to OpenRouter ---
        prompt = build_comparison_prompt(llama_result, qwen_result)

        headers = {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://agrisense.ai",
            "X-Title": "AgriSense AI"
        }

        payload = {
            "model": "qwen/qwen-2.5-72b-instruct",  # Highly capable text comparison engine
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.0,  # Deterministic
            "max_tokens": 256,
            "response_format": {"type": "json_object"}
        }

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    "https://openrouter.ai/api/v1/chat/completions",
                    headers=headers,
                    json=payload,
                )
                response.raise_for_status()
                data = response.json()
                raw_text = data["choices"][0]["message"]["content"]
        except Exception as e:
            logger.error(
                f"Comparator OpenRouter API call failed: {e}. "
                "Defaulting to mismatch (will trigger consensus).",
                exc_info=True,
            )
            return {
                "matched": False,
                "reasoning": f"Comparison API call failed: {str(e)[:100]}. Defaulting to consensus.",
                "confidence": 0,
                "llama_disease": llama_disease,
                "qwen_disease": qwen_disease,
            }

        # --- Parse comparison response ---
        try:
            parsed = extract_json(raw_text)
            matched = bool(parsed.get("matched", False))
            reasoning = str(parsed.get("reasoning", "No reasoning provided."))
            confidence = max(0, min(100, int(parsed.get("confidence", 50))))
        except (ValueError, TypeError, KeyError) as e:
            logger.warning(
                f"Comparator could not parse response: {e}. "
                f"Raw: {raw_text[:200]}. Defaulting to mismatch."
            )
            return {
                "matched": False,
                "reasoning": f"Could not parse comparison response: {str(e)[:80]}",
                "confidence": 0,
                "llama_disease": llama_disease,
                "qwen_disease": qwen_disease,
            }

        logger.info(
            f"Comparator result | matched={matched} | confidence={confidence}% | "
            f"reasoning: {reasoning[:120]}"
        )

        return {
            "matched": matched,
            "reasoning": reasoning,
            "confidence": confidence,
            "llama_disease": llama_disease,
            "qwen_disease": qwen_disease,
        }
