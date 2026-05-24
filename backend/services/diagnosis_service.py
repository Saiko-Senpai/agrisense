"""
services/diagnosis_service.py — Central AI orchestration service.

This is the heart of the AgriSense pipeline.

Model roles:
  - PRIMARY:   Gemini Vision (Google)  → always preferred on match
  - SECONDARY: Qwen Vision (Alibaba)   → cross-validation model
  - CONSENSUS: External research API   → triggered only on mismatch

Pipeline:
  1. Run Gemini (primary) and Qwen (secondary) analyses CONCURRENTLY
  2. Compare results via ComparatorService (rapidfuzz fuzzy matching)
  3a. If MATCH  → return Gemini (primary) result — it is the authoritative source
  3b. If MISMATCH → call external Consensus research API for validation
  4. Build frontend-compatible chips from stage/confidence/source
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
    Central orchestrator that coordinates the primary (Gemini),
    secondary (Qwen), and consensus (research API) services.

    On agreement: Gemini's result is returned as the authoritative source.
    On disagreement: The external research consensus API arbitrates.
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
        logger.info(f"[{request_id}] Starting dual-VLM analysis (Primary: Gemini | Secondary: Qwen)...")

        # ---------------------------------------------------------------
        # Step 1: Run Gemini (primary) and Qwen (secondary) concurrently
        # ---------------------------------------------------------------
        gemini_result, qwen_result = await asyncio.gather(
            self._safe_analyze(self._gemini.analyze, image_base64, "Gemini [PRIMARY]", request_id),
            self._safe_analyze(self._qwen.analyze, image_base64, "Qwen [SECONDARY]", request_id),
        )

        logger.info(
            f"[{request_id}] PRIMARY (Gemini) → '{gemini_result.get('disease_name')}' "
            f"({gemini_result.get('confidence')}%) | "
            f"SECONDARY (Qwen) → '{qwen_result.get('disease_name')}' "
            f"({qwen_result.get('confidence')}%)"
        )

        # ---------------------------------------------------------------
        # Step 2: Compare outputs via fuzzy matching
        # ---------------------------------------------------------------
        comparison = self._comparator.compare(gemini_result, qwen_result)
        logger.info(
            f"[{request_id}] Comparison score: {comparison['similarity_score']} | "
            f"matched: {comparison['matched']}"
        )

        # ---------------------------------------------------------------
        # Step 3a: MATCH → always use Gemini (primary) as authoritative result
        # ---------------------------------------------------------------
        if comparison["matched"]:
            # Gemini is primary — its result is the authoritative source on agreement.
            # We still log Qwen's confidence for transparency.
            final = dict(gemini_result)
            final["source"] = "gemini"
            logger.info(
                f"[{request_id}] VLMs AGREED → returning Gemini (primary) result. "
                f"Qwen corroborated with score {comparison['similarity_score']}"
            )

        # ---------------------------------------------------------------
        # Step 3b: MISMATCH → invoke external research Consensus API
        # ---------------------------------------------------------------
        else:
            logger.info(
                f"[{request_id}] VLMs DISAGREED → invoking research Consensus API to arbitrate..."
            )
            try:
                final = await self._consensus.arbitrate(gemini_result, qwen_result)
            except RuntimeError as e:
                # Fallback: if consensus API is unavailable, trust primary (Gemini)
                logger.error(
                    f"[{request_id}] Consensus API failed: {e}. "
                    "Falling back to Gemini (primary) result."
                )
                final = dict(gemini_result)
                final["source"] = "gemini"
                final["consensus_fallback"] = True

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
            "gemini": ("Gemini Primary", "chip-blue"),
            "qwen": ("Qwen Secondary", "chip-blue"),
            "consensus": ("Research Validated", "chip-green"),
        }
        label, color = source_labels.get(source, ("AI Analyzed", "chip-blue"))
        chips.append({"t": label, "c": color})

        # High spread risk chip for severe/critical stages
        if stage.lower() in ("severe", "critical"):
            chips.append({"t": "High Spread Risk", "c": "chip-red"})

        return chips
