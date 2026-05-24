"""
POST /advisory — Crop-specific AI weather advisory endpoint.

Accepts the active crop and current weather data to generate custom recommendations.
"""

import logging
import uuid
from typing import Any

from fastapi import APIRouter, HTTPException, status
from fastapi.responses import JSONResponse

from models.request_models import AdvisoryRequest
from services.advisory_service import AdvisoryService

logger = logging.getLogger("agrisense.routes.advisory")
router = APIRouter()

_advisory_service = AdvisoryService()


@router.post(
    "/",
    summary="Generate AI Crop-Specific Weather Advisory",
    response_description="AI-generated crop advisory cards",
    status_code=status.HTTP_200_OK,
)
async def generate_advisory(request: AdvisoryRequest) -> JSONResponse:
    """
    Generate highly localized and crop-specific agricultural advice using Gemini.

    Accepts:
    - **crop_name**: The selected crop (e.g. "Rice", "Tomato", "Wheat")
    - **weather_data**: The current weather object fetched from OpenWeatherMap (or mock weather)
    """
    request_id = str(uuid.uuid4())[:8]
    logger.info(
        f"[{request_id}] Advisory request | crop={request.crop_name} "
        f"| location={request.weather_data.name} "
        f"| temp={request.weather_data.main.temp}°C, humidity={request.weather_data.main.humidity}%"
    )

    try:
        # Convert Pydantic weather_data model directly to dict
        weather_dict = request.weather_data.model_dump()
        response = await _advisory_service.generate_advisory(
            crop_name=request.crop_name,
            weather_data=weather_dict,
        )
    except Exception as e:
        logger.error(f"[{request_id}] Advisory generation error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="AI weather advisory service is temporarily unavailable. Please try again.",
        )

    return JSONResponse(
        status_code=200,
        content={
            "success": True,
            "request_id": request_id,
            "data": response,
        },
    )
