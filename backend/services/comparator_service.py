"""
services/comparator_service.py — Gemini-powered diagnosis comparison service.

Uses the Gemini API (not string matching) to determine whether the
Gemini (primary) and Qwen (secondary) VLM diagnoses refer to the same disease.

Why Gemini instead of fuzzy string matching?
- Handles synonyms: "Early Blight" == "Alternaria Blight"
- Handles partial names: "Tomato Late Blight" == "Late Blight"
- Handles scientific vs. common names: "Phytophthora Blight" == "Late Blight"
- Cannot be fooled by superficially similar but different disease names
- Returns structured reasoning for auditability
"""

import asyncio
import logging
import os
from typing import Any

import google.generativeai as genai

from utils.parser import extract_json
from utils.prompts import build_comparison_prompt

logger = logging.getLogger("agrisense.services.comparator")


class ComparatorService:
    """
    Gemini-powered intelligent diagnosis comparator.

    Sends both VLM diagnosis summaries to Gemini with a structured
    plant pathology reasoning prompt and gets back a JSON decision:
      { "matched": bool, "reasoning": str, "confidence": int }

    On Gemini API failure, falls back to a conservative mismatch
    (triggering consensus) rather than a false agreement.
    """

    def __init__(self) -> None:
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            logger.warning("GEMINI_API_KEY not set. Comparator will fail on first call.")
        else:
            genai.configure(api_key=api_key)

        model_name = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
        self._model = genai.GenerativeModel(
            model_name=model_name,
            generation_config=genai.GenerationConfig(
                temperature=0.0,           # Fully deterministic — this is a binary decision
                max_output_tokens=256,     # Small response: just matched/reasoning/confidence
                response_mime_type="application/json",
            ),
        )
        logger.info(f"ComparatorService initialized with Gemini model: {model_name}")

    async def compare(
        self,
        gemini_result: dict[str, Any],
        qwen_result: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Ask Gemini to determine whether both VLM outputs describe the same disease.

        Args:
            gemini_result: Structured diagnosis dict from GeminiService (primary).
            qwen_result: Structured diagnosis dict from QwenService (secondary).

        Returns:
            dict with keys:
              - matched (bool): True if both diagnoses refer to the same disease
              - reasoning (str): Gemini's 1-2 sentence scientific justification
              - confidence (int): Gemini's confidence in its match/mismatch decision
              - gemini_disease (str): Primary model's disease name (for logging)
              - qwen_disease (str): Secondary model's disease name (for logging)

        On API failure: returns matched=False (conservative — triggers consensus)
        """
        gemini_disease = gemini_result.get("disease_name", "Unknown")
        qwen_disease = qwen_result.get("disease_name", "Unknown")

        logger.info(
            f"Comparator | Primary (Gemini): '{gemini_disease}' vs "
            f"Secondary (Qwen): '{qwen_disease}'"
        )

        # --- Quick shortcut: if both say "Healthy Plant", they trivially agree ---
        if (
            "healthy" in gemini_disease.lower()
            and "healthy" in qwen_disease.lower()
        ):
            logger.info("Comparator | Both models agree: Healthy Plant (shortcut match)")
            return {
                "matched": True,
                "reasoning": "Both models independently identified the plant as healthy.",
                "confidence": 100,
                "gemini_disease": gemini_disease,
                "qwen_disease": qwen_disease,
            }

        # --- Build and send comparison prompt to Gemini ---
        prompt = build_comparison_prompt(gemini_result, qwen_result)

        try:
            response = await asyncio.get_event_loop().run_in_executor(
                None, lambda: self._model.generate_content(prompt)
            )
            raw_text = response.text
        except Exception as e:
            logger.error(
                f"Comparator Gemini API call failed: {e}. "
                "Defaulting to mismatch (will trigger consensus).",
                exc_info=True,
            )
            return {
                "matched": False,
                "reasoning": f"Comparison API call failed: {str(e)[:100]}. Defaulting to consensus.",
                "confidence": 0,
                "gemini_disease": gemini_disease,
                "qwen_disease": qwen_disease,
            }

        # --- Parse the Gemini comparison response ---
        try:
            parsed = extract_json(raw_text)
            matched = bool(parsed.get("matched", False))
            reasoning = str(parsed.get("reasoning", "No reasoning provided."))
            confidence = max(0, min(100, int(parsed.get("confidence", 50))))
        except (ValueError, TypeError, KeyError) as e:
            logger.warning(
                f"Comparator could not parse Gemini response: {e}. "
                f"Raw: {raw_text[:200]}. Defaulting to mismatch."
            )
            return {
                "matched": False,
                "reasoning": f"Could not parse comparison response: {str(e)[:80]}",
                "confidence": 0,
                "gemini_disease": gemini_disease,
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
            "gemini_disease": gemini_disease,
            "qwen_disease": qwen_disease,
        }
