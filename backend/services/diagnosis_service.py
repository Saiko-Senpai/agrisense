"""
services/diagnosis_service.py — Central AI orchestration service.

This is the heart of the AgriSense pipeline.

Model roles:
  - PRIMARY:   Llama Vision (Meta)     → always preferred on match
  - SECONDARY: Qwen Vision (Alibaba)   → cross-validation model
  - CONSENSUS: External research API   → triggered only on mismatch

Pipeline:
  1. Run Llama (primary) and Qwen (secondary) analyses CONCURRENTLY
  2. Compare results via ComparatorService
  3a. If MATCH  → return Llama (primary) result — it is the authoritative source
  3b. If MISMATCH → call external Consensus research API for validation
  4. Build frontend-compatible chips from stage/confidence/source
  5. Return fully structured final diagnosis
"""

import asyncio
import logging
from typing import Any

from services.comparator_service import ComparatorService
from services.consensus_service import ConsensusService
from services.llama_service import LlamaService
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
    Central orchestrator that coordinates the primary (Llama),
    secondary (Qwen), and consensus (research API) services.

    On agreement: Llama's result is returned as the authoritative source.
    On disagreement: The external research consensus API arbitrates.
    """

    def __init__(self) -> None:
        self._llama = LlamaService()
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
        logger.info(f"[{request_id}] Starting dual-VLM analysis (Primary: Llama | Secondary: Qwen)...")

        # ---------------------------------------------------------------
        # Step 1: Run Llama (primary) and Qwen (secondary) concurrently
        # ---------------------------------------------------------------
        llama_result, qwen_result = await asyncio.gather(
            self._safe_analyze(self._llama.analyze, image_base64, "Llama [PRIMARY]", request_id),
            self._safe_analyze(self._qwen.analyze, image_base64, "Qwen [SECONDARY]", request_id),
        )

        logger.info(
            f"[{request_id}] PRIMARY (Llama) → '{llama_result.get('disease_name')}' "
            f"({llama_result.get('confidence')}%) | "
            f"SECONDARY (Qwen) → '{qwen_result.get('disease_name')}' "
            f"({qwen_result.get('confidence')}%)"
        )

        # ---------------------------------------------------------------
        # Step 2: Llama compares both outputs (no string matching)
        # ---------------------------------------------------------------
        comparison = await self._comparator.compare(llama_result, qwen_result)
        logger.info(
            f"[{request_id}] Llama comparator | matched={comparison['matched']} | "
            f"confidence={comparison['confidence']}% | "
            f"reasoning: {comparison['reasoning'][:100]}"
        )

        # ---------------------------------------------------------------
        # Step 3a: MATCH → always use Llama (primary) as authoritative result
        # ---------------------------------------------------------------
        if comparison["matched"]:
            # Llama is primary — its result is the authoritative source on agreement.
            final = dict(llama_result)
            final["source"] = "llama"
            logger.info(
                f"[{request_id}] VLMs AGREED → returning Llama (primary) result. "
                f"Qwen corroborated. Comparator confidence: {comparison['confidence']}%"
            )

        # ---------------------------------------------------------------
        # Step 3b: MISMATCH → invoke external research Consensus API
        # ---------------------------------------------------------------
        else:
            logger.info(
                f"[{request_id}] VLMs DISAGREED → invoking research Consensus API to arbitrate..."
            )
            try:
                final = await self._consensus.arbitrate(llama_result, qwen_result)
            except RuntimeError as e:
                # Fallback: if consensus API is unavailable, trust primary (Llama)
                logger.error(
                    f"[{request_id}] Consensus API failed: {e}. "
                    "Falling back to Llama (primary) result."
                )
                final = dict(llama_result)
                final["source"] = "llama"
                final["consensus_fallback"] = True

        # ---------------------------------------------------------------
        # Step 4: Enrich with comparison metadata and frontend chips
        # ---------------------------------------------------------------
        final["comparison_matched"] = comparison["matched"]
        final["comparison_confidence"] = comparison["confidence"]
        final["comparison_reasoning"] = comparison["reasoning"]
        final["chips"] = self._build_chips(final)

        # Dynamically extract and inject crop common name from disease/description
        final["crop"] = self._resolve_crop_name(final.get("disease_name", ""), final.get("description", ""))

        # Rename disease_name → disease and map description to text to match frontend TypeScript type
        final["disease"] = final.pop("disease_name", "Unknown Disease")
        final["text"] = final.get("description", "No description provided.")

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
            "llama": ("Llama Primary", "chip-blue"),
            "qwen": ("Qwen Secondary", "chip-blue"),
            "consensus": ("Research Validated", "chip-green"),
        }
        label, color = source_labels.get(source, ("AI Analyzed", "chip-blue"))
        chips.append({"t": label, "c": color})

        # High spread risk chip for severe/critical stages
        if stage.lower() in ("severe", "critical"):
            chips.append({"t": "High Spread Risk", "c": "chip-red"})

        return chips

    def _resolve_crop_name(self, disease: str, description: str) -> str:
        """
        Dynamically extracts the crop's common name from the disease or description
        to ensure crop-level context is always available.
        """
        disease_lower = disease.lower()
        desc_lower = description.lower()
        
        crop_keywords = ["rice", "wheat", "potato", "tomato", "cotton", "maize", "corn", "sugarcane", "onion", "mustard"]
        
        # Check disease name first
        for crop in crop_keywords:
            if crop in disease_lower:
                return crop.capitalize()
                
        # Check description text next
        for crop in crop_keywords:
            if crop in desc_lower:
                return crop.capitalize()
                
        return "Crop"
