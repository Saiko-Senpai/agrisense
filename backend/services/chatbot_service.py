"""
services/chatbot_service.py — Agriculture-only context-aware chatbot service.

Uses Llama as the language model backend.

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
import httpx
from typing import Any

from models.request_models import ChatMessage
from utils.prompts import build_chatbot_system_prompt

logger = logging.getLogger("agrisense.services.chatbot")

# Keywords that strongly suggest an agriculture query
_AGRICULTURE_KEYWORDS = {
    "crop", "plant", "disease", "pest", "fertilizer", "irrigation",
    "harvest", "soil", "seed", "blight", "mildew", "rust", "fungus",
    "bacteria", "virus", "nematode", "insecticide", "herbicide", "farm",
    "farmer", "agriculture", "paddy", "rice", "wheat", "potato", "tomato",
    "maize", "cotton", "sugarcane", "onion", "mustard", "spray", "yield",
    "weed", "compost", "organic", "manure", "drip", "mulch", "greenhouse",
    "temperature", "humidity", "rain", "season", "sow", "grow", "treat",
    "prevent", "cure", "symptom", "leaf", "root", "stem", "flower", "fruit",
    "pesticide", "danger", "dangerous", "spread", "treatment"
}

_OFF_TOPIC_RESPONSE = (
    "I can only assist with agriculture and crop-related questions. "
    "Please ask me about crop diseases, farming practices, fertilizers, "
    "irrigation, or pest control."
)


class ChatbotService:
    """
    Context-aware agricultural chatbot powered by Qwen on OpenRouter.

    The chatbot:
    1. Pre-screens queries for agriculture relevance (unless crop/disease context is active)
    2. Injects crop + disease context into the system prompt
    3. Sends the conversation history to OpenRouter Qwen for high-fidelity responses
    """

    def __init__(self) -> None:
        self._api_key = os.getenv("QWEN_API_KEY")
        if not self._api_key:
            logger.warning("QWEN_API_KEY not set. Chatbot service will fail on first call.")
        logger.info("ChatbotService initialized with Qwen OpenRouter engine.")

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
            disease_context: Optional detected disease context.
            conversation_history: Prior conversation turns.

        Returns:
            dict with keys: reply, is_agriculture_related, crop_context, disease_context.
        """
        # If the user is actively inside a crop/disease context details page,
        # we bypass the keyword filter to ensure all follow-up questions work perfectly!
        is_contextual = bool(crop_context or disease_context)
        is_relevant = is_contextual or self._is_agriculture_related(message)

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

        # --- Construct message payload for OpenRouter OpenAI format ---
        messages_payload = [{"role": "system", "content": system_prompt}]
        
        # Add conversation history
        for msg in conversation_history or []:
            role = "assistant" if msg.role == "assistant" else "user"
            messages_payload.append({"role": role, "content": msg.content})
            
        # Add the current user message
        messages_payload.append({"role": "user", "content": message})

        headers = {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://agrisense.ai",
            "X-Title": "AgriSense AI"
        }

        payload = {
            "model": "qwen/qwen-2.5-72b-instruct",  # Ultra high-performance Qwen text model
            "messages": messages_payload,
            "temperature": 0.5,
            "max_tokens": 1024,
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
                reply = data["choices"][0]["message"]["content"].strip()
        except Exception as e:
            logger.error(f"Chatbot OpenRouter API call failed: {e}", exc_info=True)
            # Safe agronomical fallback message in case of network interruptions
            reply = "I apologize, but I am experiencing a temporary connection issue. Please ensure the crop has optimal aeration, avoid excess nitrogen, and feel free to ask me again shortly!"

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
