"""
Pydantic response models for AgriSense API endpoints.
"""

from typing import Any, Literal, Optional

from pydantic import BaseModel, Field


class DiagnosisChip(BaseModel):
    """A UI display chip/tag for the frontend."""

    t: str = Field(..., description="Chip label text (e.g. 'Severe Stage')")
    c: str = Field(..., description="Chip color class (chip-red | chip-green | chip-blue | chip-yellow)")


class DiagnosisData(BaseModel):
    """
    The structured crop disease diagnosis payload.

    Mirrors the frontend's DiseaseResult type exactly for seamless integration.
    """

    disease_name: str = Field(..., description="Common name of the detected disease")
    pathogen: str = Field(..., description="Scientific pathogen name (e.g. 'Phytophthora infestans')")
    confidence: int = Field(..., ge=0, le=100, description="Confidence percentage (0–100)")
    stage: str = Field(..., description="Disease growth stage (e.g. 'Early', 'Severe')")
    description: str = Field(..., description="Concise description of the disease and its impact")
    treatment: list[str] = Field(default_factory=list, description="Ordered list of treatment steps")
    prevention: list[str] = Field(default_factory=list, description="Ordered list of prevention measures")
    chips: list[DiagnosisChip] = Field(default_factory=list, description="Frontend display chips/tags")
    source: Literal["gemini", "qwen", "consensus"] = Field(
        ..., description="Which AI model produced the final diagnosis"
    )
    similarity_score: Optional[float] = Field(
        default=None,
        description="Fuzzy similarity score between Gemini and Qwen outputs (0–100)",
    )
    matched: Optional[bool] = Field(
        default=None,
        description="Whether the two VLM outputs matched without needing consensus",
    )


class DiagnosisResponse(BaseModel):
    """Top-level response envelope for POST /analyze."""

    success: bool = True
    request_id: str
    data: DiagnosisData


class ChatData(BaseModel):
    """Chatbot response payload."""

    reply: str = Field(..., description="The AI assistant's reply text")
    is_agriculture_related: bool = Field(
        ..., description="Whether the query was recognized as agriculture-related"
    )
    crop_context: Optional[str] = Field(default=None, description="Active crop context")
    disease_context: Optional[str] = Field(default=None, description="Active disease context")


class ChatResponse(BaseModel):
    """Top-level response envelope for POST /chat."""

    success: bool = True
    request_id: str
    data: ChatData
