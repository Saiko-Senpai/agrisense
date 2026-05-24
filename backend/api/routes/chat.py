"""
POST /chat — Context-aware agricultural chatbot endpoint.

The chatbot:
- Accepts user messages, optional crop context, and optional disease context.
- Strictly limits responses to agriculture-related queries.
- Rejects unrelated topics with a polite redirect message.
"""

import logging
import uuid

from fastapi import APIRouter, HTTPException, status
from fastapi.responses import JSONResponse

from models.request_models import ChatRequest
from models.response_models import ChatResponse
from services.chatbot_service import ChatbotService

logger = logging.getLogger("agrisense.routes.chat")
router = APIRouter()

_chatbot_service = ChatbotService()


@router.post(
    "/",
    summary="Agricultural AI chatbot",
    response_model=ChatResponse,
    response_description="AI-generated farming guidance",
    status_code=status.HTTP_200_OK,
)
async def chat(request: ChatRequest) -> JSONResponse:
    """
    Send a message to the AgriSense agricultural AI assistant.

    The assistant is context-aware:
    - **crop_context**: name of the crop the user is growing (e.g. "tomato")
    - **disease_context**: detected disease from a prior scan (e.g. "Late Blight")

    The assistant **only** answers agriculture-related questions.
    Off-topic queries receive a graceful redirect message.
    """
    request_id = str(uuid.uuid4())[:8]
    logger.info(
        f"[{request_id}] Chat request | crop={request.crop_context} "
        f"| disease={request.disease_context} | msg={request.message[:60]}..."
    )

    try:
        response = await _chatbot_service.respond(
            message=request.message,
            crop_context=request.crop_context,
            disease_context=request.disease_context,
            conversation_history=request.conversation_history,
        )
    except Exception as e:
        logger.error(f"[{request_id}] Chatbot error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Chatbot service is temporarily unavailable. Please try again.",
        )

    return JSONResponse(
        status_code=200,
        content={
            "success": True,
            "request_id": request_id,
            "data": response,
        },
    )
