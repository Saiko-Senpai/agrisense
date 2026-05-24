"""
services/comparator_service.py — Fuzzy similarity comparator for Gemini vs Qwen outputs.

Uses rapidfuzz for robust string similarity matching.
Compares disease names and stages to determine whether both VLMs agree
on the diagnosis, allowing for minor naming variations.

Example:
    "Early Blight" vs "Tomato Early Blight" → MATCH (high substring similarity)
    "Late Blight"  vs "Powdery Mildew"      → MISMATCH
"""

import logging
import os
from typing import Any

from rapidfuzz import fuzz, process

logger = logging.getLogger("agrisense.services.comparator")

# Similarity threshold (0–100) above which two diagnoses are considered a match
MATCH_THRESHOLD = int(os.getenv("MATCH_THRESHOLD", 75))

# Weight factors for the composite similarity score
DISEASE_NAME_WEIGHT = 0.75   # Disease name is the primary signal
STAGE_WEIGHT = 0.25          # Stage adds context but is secondary


class ComparatorService:
    """
    Compares two VLM diagnosis outputs using fuzzy string matching.

    Scoring strategy:
    - Compute token_set_ratio on disease names (handles reordering and substrings)
    - Compute partial_ratio on disease stages
    - Combine into a weighted composite score
    - Return match=True if composite score >= MATCH_THRESHOLD
    """

    def compare(
        self,
        gemini_result: dict[str, Any],
        qwen_result: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Compare two diagnosis dictionaries for agreement.

        Args:
            gemini_result: Structured diagnosis dict from GeminiService.
            qwen_result: Structured diagnosis dict from QwenService.

        Returns:
            dict with keys:
              - matched (bool): True if diagnoses agree
              - similarity_score (float): Composite score 0–100
              - disease_name_score (float): Disease name similarity 0–100
              - stage_score (float): Stage similarity 0–100
              - threshold (int): The configured MATCH_THRESHOLD
        """
        gemini_disease = (gemini_result.get("disease_name") or "").strip()
        qwen_disease = (qwen_result.get("disease_name") or "").strip()
        gemini_stage = (gemini_result.get("stage") or "").strip()
        qwen_stage = (qwen_result.get("stage") or "").strip()

        # --- Disease name similarity ---
        # token_set_ratio handles "Tomato Early Blight" vs "Early Blight" correctly
        disease_score = fuzz.token_set_ratio(
            gemini_disease.lower(), qwen_disease.lower()
        )

        # --- Stage similarity ---
        stage_score = fuzz.partial_ratio(
            gemini_stage.lower(), qwen_stage.lower()
        ) if gemini_stage and qwen_stage else 100.0

        # --- Weighted composite score ---
        composite = (
            disease_score * DISEASE_NAME_WEIGHT
            + stage_score * STAGE_WEIGHT
        )

        matched = composite >= MATCH_THRESHOLD

        logger.info(
            f"Comparator | '{gemini_disease}' vs '{qwen_disease}' | "
            f"disease={disease_score:.1f} stage={stage_score:.1f} "
            f"composite={composite:.1f} | matched={matched}"
        )

        return {
            "matched": matched,
            "similarity_score": round(composite, 1),
            "disease_name_score": round(disease_score, 1),
            "stage_score": round(stage_score, 1),
            "threshold": MATCH_THRESHOLD,
        }

    def pick_best(
        self,
        gemini_result: dict[str, Any],
        qwen_result: dict[str, Any],
    ) -> tuple[dict[str, Any], str]:
        """
        When outputs match, pick the one with the higher confidence score.

        Returns:
            (best_result_dict, source_label) where source_label is "gemini" or "qwen".
        """
        g_conf = gemini_result.get("confidence", 0)
        q_conf = qwen_result.get("confidence", 0)

        if g_conf >= q_conf:
            logger.debug(f"Picked Gemini result (confidence {g_conf}% >= {q_conf}%)")
            return gemini_result, "gemini"
        else:
            logger.debug(f"Picked Qwen result (confidence {q_conf}% > {g_conf}%)")
            return qwen_result, "qwen"
