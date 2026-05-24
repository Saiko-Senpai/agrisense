"""
Pydantic request models for AgriSense API endpoints.
"""

from typing import Any, Optional

from pydantic import BaseModel, Field, field_validator


class ChatMessage(BaseModel):
    """A single message in a conversation history."""

    role: str = Field(..., description="'user' or 'assistant'")
    content: str = Field(..., description="Message content")


class ChatRequest(BaseModel):
    """
    Request body for POST /chat.

    All fields except `message` are optional context injectors
    that help the AI provide more relevant agricultural advice.
    """

    message: str = Field(
        ...,
        min_length=1,
        max_length=2000,
        description="The user's question or message",
        examples=["What is the best treatment for late blight?"],
    )
    crop_context: Optional[str] = Field(
        default=None,
        max_length=100,
        description="Name of the crop currently under discussion (e.g. 'tomato', 'wheat')",
        examples=["tomato"],
    )
    disease_context: Optional[str] = Field(
        default=None,
        max_length=200,
        description="Disease detected from a prior scan (e.g. 'Late Blight')",
        examples=["Late Blight"],
    )
    conversation_history: list[ChatMessage] = Field(
        default_factory=list,
        max_length=20,
        description="Prior conversation turns for context continuity (max 20 turns)",
    )

    @field_validator("message")
    @classmethod
    def message_not_blank(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Message cannot be empty or whitespace only.")
        return v.strip()


class AnalyzeRequest(BaseModel):
    """
    Metadata accompanying a POST /analyze image upload.

    This model is used if the frontend sends additional JSON metadata
    alongside the multipart image. Currently optional.
    """

    crop_hint: Optional[str] = Field(
        default=None,
        max_length=100,
        description="Optional user-provided crop name to assist analysis (e.g. 'potato')",
        examples=["potato"],
    )
