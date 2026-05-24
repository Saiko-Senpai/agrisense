"""
services/diagnosis_service.py — Central AI orchestration service.

This is the heart of the AgriSense pipeline.

Pipeline:
  1. Run Gemini and Qwen analyses CONCURRENTLY (asyncio.gather)
  2. Compare results via ComparatorService (fuzzy matching)
  3a. If MATCH → pick the higher-confidence result → return with source tag
  3b. If MISMATCH → invoke ConsensusService → return consensus result
  4. Build frontend-compatible chips from stage/confidence
  5. Return fully structured final diagnosis
"""

import asyncio
import logging
from typing import Any

from services.comparator_service import ComparatorService
from services.consensus_service import ConsensusService
from services.gemini_service import GeminiService
from services.qwen_service import QwenService

logger = logging.getLogger("agrisense.services.diagnosis")


# Map disease stages to frontend chip colors
_STAGE_CHIP_COLORS: dict[str, str] = {
    "early": "chip-green",
    "moderate": "chip-yellow",
    "severe": "chip-red",
    "critical": "chip-red",
    "unknown": "chip-blue",
    "healthy": "chip-green",
}


class DiagnosisService:
    """
    Central orchestrator that coordinates all AI services and returns
    a fully structured, frontend-ready diagnosis dictionary.
    """

    def __init__(self) -> None:
        self._gemini = GeminiService()
        self._qwen = QwenService()
        self._comparator = ComparatorService()
        self._consensus = ConsensusService()

    async def run(
        self,
        image_base64: str,
        image_bytes: bytes,
        request_id: str = "N/A",
    ) -> dict[str, Any]:
        """
        Execute the full dual-VLM → comparator → (optional) consensus pipeline.

        Args:
            image_base64: Base64-encoded, preprocessed image.
            image_bytes: Original raw image bytes (reserved for future use).
            request_id: Logging correlation ID.

        Returns:
            Fully structured diagnosis dictionary ready for the API response.
        """
        logger.info(f"[{request_id}] Starting dual-VLM analysis...")

        # ---------------------------------------------------------------
        # Step 1: Run Gemini and Qwen concurrently
        # ---------------------------------------------------------------
        gemini_result, qwen_result = await asyncio.gather(
            self._safe_analyze(self._gemini.analyze, image_base64, "Gemini", request_id),
            self._safe_analyze(self._qwen.analyze, image_base64, "Qwen", request_id),
        )

        logger.info(
            f"[{request_id}] Gemini → {gemini_result.get('disease_name')} "
            f"({gemini_result.get('confidence')}%) | "
            f"Qwen → {qwen_result.get('disease_name')} "
            f"({qwen_result.get('confidence')}%)"
        )

        # ---------------------------------------------------------------
        # Step 2: Compare outputs
        # ---------------------------------------------------------------
        comparison = self._comparator.compare(gemini_result, qwen_result)
        logger.info(
            f"[{request_id}] Comparison score: {comparison['similarity_score']} | "
            f"matched: {comparison['matched']}"
        )

        # ---------------------------------------------------------------
        # Step 3a: Match → pick the higher-confidence result
        # ---------------------------------------------------------------
        if comparison["matched"]:
            best, source = self._comparator.pick_best(gemini_result, qwen_result)
            final = dict(best)
            final["source"] = source
            logger.info(f"[{request_id}] VLMs agreed → using {source} result")

        # ---------------------------------------------------------------
        # Step 3b: Mismatch → invoke consensus AI
        # ---------------------------------------------------------------
        else:
            logger.info(f"[{request_id}] VLMs disagreed → invoking consensus AI...")
            try:
                final = await self._consensus.arbitrate(gemini_result, qwen_result)
            except RuntimeError as e:
                # Fallback: if consensus fails, use the higher-confidence model
                logger.error(
                    f"[{request_id}] Consensus AI failed: {e}. "
                    "Falling back to higher-confidence VLM result."
                )
                best, source = self._comparator.pick_best(gemini_result, qwen_result)
                final = dict(best)
                final["source"] = source

        # ---------------------------------------------------------------
        # Step 4: Enrich with comparison metadata and frontend chips
        # ---------------------------------------------------------------
        final["similarity_score"] = comparison["similarity_score"]
        final["matched"] = comparison["matched"]
        final["chips"] = self._build_chips(final)

        # Ensure disease_name key matches frontend expectation
        # (frontend uses "disease" not "disease_name")
        final["disease"] = final.pop("disease_name", "Unknown Disease")

        return final

    # -----------------------------------------------------------------------
    # Helpers
    # -----------------------------------------------------------------------

    async def _safe_analyze(
        self,
        fn,
        image_base64: str,
        model_name: str,
        request_id: str,
    ) -> dict[str, Any]:
        """
        Call an analysis function with error isolation.

        On failure, returns a fallback 'Unknown Disease' result so the
        pipeline can continue with partial data rather than failing entirely.
        """
        try:
            return await fn(image_base64)
        except Exception as e:
            logger.error(
                f"[{request_id}] {model_name} analysis failed: {e}",
                exc_info=True,
            )
            return {
                "disease_name": "Analysis Error",
                "pathogen": "Unknown",
                "confidence": 0,
                "stage": "Unknown",
                "description": f"{model_name} analysis failed: {str(e)[:100]}",
                "treatment": [],
                "prevention": [],
            }

    def _build_chips(self, result: dict[str, Any]) -> list[dict[str, str]]:
        """
        Build frontend display chips from the diagnosis result.

        Returns a list of {t: label, c: color_class} dicts.
        """
        chips: list[dict[str, str]] = []
        stage = (result.get("stage") or "Unknown").strip()
        confidence = result.get("confidence", 0)
        source = result.get("source", "unknown")

        # Stage chip
        stage_color = _STAGE_CHIP_COLORS.get(stage.lower(), "chip-blue")
        chips.append({"t": f"{stage} Stage", "c": stage_color})

        # Confidence chip
        if confidence >= 85:
            chips.append({"t": "High Confidence", "c": "chip-green"})
        elif confidence >= 60:
            chips.append({"t": "Moderate Confidence", "c": "chip-yellow"})
        else:
            chips.append({"t": "Low Confidence", "c": "chip-red"})

        # Source chip
        source_labels = {
            "gemini": ("Gemini Verified", "chip-blue"),
            "qwen": ("Qwen Verified", "chip-blue"),
            "consensus": ("Consensus Validated", "chip-green"),
        }
        label, color = source_labels.get(source, ("AI Analyzed", "chip-blue"))
        chips.append({"t": label, "c": color})

        # High spread risk chip for severe/critical stages
        if stage.lower() in ("severe", "critical"):
            chips.append({"t": "High Spread Risk", "c": "chip-red"})

        return chips
