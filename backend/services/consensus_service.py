"""
services/consensus_service.py — Consensus AI arbitration service.

Only triggered when Gemini and Qwen produce conflicting diagnoses.

The consensus model (configurable — defaults to Gemini 1.5 Pro) acts as a
senior research scientist, evaluating both diagnoses and providing a
scientifically validated final determination with research-backed reasoning.
"""

import asyncio
import logging
import os
from typing import Any

import google.generativeai as genai

from utils.parser import extract_json, validate_diagnosis
from utils.prompts import build_consensus_prompt

logger = logging.getLogger("agrisense.services.consensus")


class ConsensusService:
    """
    Uses an LLM to arbitrate between conflicting VLM diagnoses.

    The consensus model receives both diagnoses and is instructed to:
    - Reason scientifically about which is more plausible
    - Merge similar diagnoses (e.g. "Early Blight" vs "Alternaria Blight")
    - Provide a fully validated treatment and prevention plan
    - Include a brief reasoning explanation
    """

    def __init__(self) -> None:
        api_key = os.getenv("CONSENSUS_API_KEY") or os.getenv("GEMINI_API_KEY")
        if not api_key:
            logger.warning(
                "CONSENSUS_API_KEY not set. Falling back to GEMINI_API_KEY. "
                "Consensus service may not function if neither is set."
            )
        else:
            genai.configure(api_key=api_key)

        model_name = os.getenv("CONSENSUS_MODEL", "gemini-1.5-pro")
        self._model = genai.GenerativeModel(
            model_name=model_name,
            generation_config=genai.GenerationConfig(
                temperature=0.2,        # Slightly higher temp for better reasoning
                max_output_tokens=2048,
                response_mime_type="application/json",
            ),
        )
        logger.info(f"ConsensusService initialized with model: {model_name}")

    async def arbitrate(
        self,
        gemini_result: dict[str, Any],
        qwen_result: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Resolve a conflict between Gemini and Qwen diagnoses.

        Args:
            gemini_result: Structured diagnosis from GeminiService.
            qwen_result: Structured diagnosis from QwenService.

        Returns:
            A validated diagnosis dictionary with an additional "source" key
            set to "consensus" and an optional "reasoning" field.

        Raises:
            RuntimeError: On API failure or unparseable response.
        """
        logger.info(
            f"Consensus triggered | Gemini: '{gemini_result.get('disease_name')}' "
            f"vs Qwen: '{qwen_result.get('disease_name')}'"
        )

        prompt = build_consensus_prompt(gemini_result, qwen_result)

        try:
            response = await asyncio.get_event_loop().run_in_executor(
                None, lambda: self._model.generate_content(prompt)
            )
        except Exception as e:
            logger.error(f"Consensus API call failed: {e}", exc_info=True)
            raise RuntimeError(f"Consensus AI error: {e}") from e

        raw_text = ""
        try:
            raw_text = response.text
        except Exception as e:
            raise RuntimeError(f"Consensus returned an empty or blocked response: {e}") from e

        logger.debug(f"Consensus raw response (first 400 chars): {raw_text[:400]}")

        try:
            parsed = extract_json(raw_text)
            validated = validate_diagnosis(parsed)
        except ValueError as e:
            raise RuntimeError(f"Consensus response parsing failed: {e}") from e

        # Tag the source for traceability
        validated["source"] = "consensus"

        logger.info(
            f"Consensus result: '{validated['disease_name']}' "
            f"({validated['confidence']}% confidence) | "
            f"Reasoning: {validated.get('reasoning', 'N/A')[:100]}"
        )

        return validated
