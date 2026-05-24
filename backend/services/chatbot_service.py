"""
services/chatbot_service.py — Agriculture-only context-aware chatbot service.

Uses Gemini as the language model backend.

Features:
- Strict agriculture-only domain restriction (enforced via system prompt)
- Crop context injection (e.g. "I'm growing tomatoes")
- Disease context injection (e.g. "I detected Late Blight")
- Conversation history support (rolling window)
- Graceful off-topic rejection
"""

import asyncio
import logging
import os
from typing import Any

import google.generativeai as genai

from models.request_models import ChatMessage
from utils.prompts import build_chatbot_system_prompt

logger = logging.getLogger("agrisense.services.chatbot")

# Keywords that strongly suggest an off-topic query
# We do a quick pre-check before even calling the LLM to save cost + latency
_AGRICULTURE_KEYWORDS = {
    "crop", "plant", "disease", "pest", "fertilizer", "irrigation",
    "harvest", "soil", "seed", "blight", "mildew", "rust", "fungus",
    "bacteria", "virus", "nematode", "insecticide", "herbicide", "farm",
    "farmer", "agriculture", "paddy", "rice", "wheat", "potato", "tomato",
    "maize", "cotton", "sugarcane", "onion", "mustard", "spray", "yield",
    "weed", "compost", "organic", "manure", "drip", "mulch", "greenhouse",
    "temperature", "humidity", "rain", "season", "sow", "grow", "treat",
    "prevent", "cure", "symptom", "leaf", "root", "stem", "flower", "fruit",
}

_OFF_TOPIC_RESPONSE = (
    "I can only assist with agriculture and crop-related questions. "
    "Please ask me about crop diseases, farming practices, fertilizers, "
    "irrigation, or pest control."
)


class ChatbotService:
    """
    Context-aware agricultural chatbot powered by Gemini.

    The chatbot:
    1. Pre-screens queries for agriculture relevance (fast keyword heuristic)
    2. Injects crop + disease context into the system prompt
    3. Sends the conversation history for multi-turn coherence
    4. Returns the AI reply along with context metadata
    """

    def __init__(self) -> None:
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            logger.warning("GEMINI_API_KEY not set. Chatbot service will fail on first call.")
        else:
            genai.configure(api_key=api_key)

        self._model_name = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
        logger.info(f"ChatbotService initialized with model: {self._model_name}")

    async def respond(
        self,
        message: str,
        crop_context: str | None = None,
        disease_context: str | None = None,
        conversation_history: list[ChatMessage] | None = None,
    ) -> dict[str, Any]:
        """
        Generate an agriculture-focused response to the user's message.

        Args:
            message: The user's current input.
            crop_context: Optional active crop (e.g. "tomato").
            disease_context: Optional detected disease (e.g. "Late Blight").
            conversation_history: Prior conversation turns for multi-turn context.

        Returns:
            dict with keys: reply, is_agriculture_related, crop_context, disease_context.
        """
        # --- Quick relevance pre-screening ---
        is_relevant = self._is_agriculture_related(message)

        if not is_relevant:
            logger.info(f"Off-topic query rejected: '{message[:60]}'")
            return {
                "reply": _OFF_TOPIC_RESPONSE,
                "is_agriculture_related": False,
                "crop_context": crop_context,
                "disease_context": disease_context,
            }

        # --- Build system prompt with active context ---
        system_prompt = build_chatbot_system_prompt(crop_context, disease_context)

        # --- Construct the model with system instructions ---
        model = genai.GenerativeModel(
            model_name=self._model_name,
            system_instruction=system_prompt,
            generation_config=genai.GenerationConfig(
                temperature=0.6,        # Moderate creativity for conversational responses
                max_output_tokens=1024,
            ),
        )

        # --- Build conversation history for multi-turn ---
        history = self._build_history(conversation_history or [])

        # --- Start chat and send message ---
        try:
            chat_session = model.start_chat(history=history)
            response = await asyncio.get_event_loop().run_in_executor(
                None, lambda: chat_session.send_message(message)
            )
            reply = response.text.strip()
        except Exception as e:
            logger.error(f"Chatbot API call failed: {e}", exc_info=True)
            raise RuntimeError(f"Chatbot API error: {e}") from e

        logger.debug(f"Chatbot reply (first 100 chars): {reply[:100]}")

        return {
            "reply": reply,
            "is_agriculture_related": True,
            "crop_context": crop_context,
            "disease_context": disease_context,
        }

    # -----------------------------------------------------------------------
    # Helpers
    # -----------------------------------------------------------------------

    def _is_agriculture_related(self, message: str) -> bool:
        """
        Fast keyword-based pre-screening to avoid sending off-topic
        queries to the LLM (saves cost and latency).

        Returns True if the message likely concerns agriculture.
        For short/ambiguous messages, defaults to True (let the LLM decide via system prompt).
        """
        words = message.lower().split()

        # If fewer than 4 words and no clear off-topic signal, let the LLM handle it
        if len(words) < 4:
            return True

        # Check for any agriculture keyword
        for word in words:
            # Strip punctuation from word
            clean = word.strip(".,?!;:'\"()")
            if clean in _AGRICULTURE_KEYWORDS:
                return True

        # Longer messages with no agriculture keywords are flagged as off-topic
        return False

    def _build_history(self, history: list[ChatMessage]) -> list[dict]:
        """
        Convert ChatMessage pydantic models to Gemini SDK history format.

        Gemini expects: [{"role": "user"|"model", "parts": ["text"]}]
        """
        # Map "assistant" role to "model" for Gemini SDK compatibility
        return [
            {
                "role": "model" if msg.role == "assistant" else "user",
                "parts": [msg.content],
            }
            for msg in history
        ]
