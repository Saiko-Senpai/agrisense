"""
POST /analyze — Crop disease image analysis endpoint.

Pipeline:
  1. Validate and preprocess the uploaded image
  2. Run Qwen Vision analysis concurrently with Llama Vision analysis
  3. Compare both outputs via the comparator service
  4. If match → return verified diagnosis
  5. If mismatch → invoke consensus service and return validated diagnosis
"""

import logging
import uuid
from pathlib import Path

from fastapi import APIRouter, File, HTTPException, UploadFile, status
from fastapi.responses import JSONResponse

from models.response_models import DiagnosisResponse
from services.diagnosis_service import DiagnosisService
from utils.image_utils import ImageProcessor
from utils.validators import validate_image_upload

logger = logging.getLogger("agrisense.routes.analyze")
router = APIRouter()

# Singleton service instance
_diagnosis_service = DiagnosisService()
_image_processor = ImageProcessor()


@router.post(
    "/",
    summary="Analyze crop disease from image",
    response_model=DiagnosisResponse,
    response_description="Structured crop disease diagnosis result",
    status_code=status.HTTP_200_OK,
)
async def analyze_crop(
    image: UploadFile = File(..., description="Crop image in JPG or PNG format"),
) -> JSONResponse:
    """
    Upload a crop image to receive an AI-powered disease diagnosis.

    The endpoint runs the dual-VLM pipeline:
    - **Qwen Vision** and **Llama Vision** analyze the image in parallel.
    - A **comparator** scores similarity between the two outputs.
    - On disagreement, a **consensus AI** arbitrates the final diagnosis.

    Returns a fully structured JSON response with:
    - disease name, pathogen, confidence score
    - growth stage, severity tags
    - treatment and prevention plans
    """
    request_id = str(uuid.uuid4())[:8]
    logger.info(f"[{request_id}] Received image: {image.filename} ({image.content_type})")

    # --- Validate file format and size ---
    try:
        image_bytes = await image.read()
        validate_image_upload(image_bytes, image.content_type, image.filename)
    except ValueError as e:
        logger.warning(f"[{request_id}] Validation failed: {e}")
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))

    # --- Preprocess: resize, compress, convert to base64 ---
    try:
        processed = await _image_processor.preprocess(image_bytes)
    except Exception as e:
        logger.error(f"[{request_id}] Image preprocessing failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Image preprocessing failed. Ensure the image is not corrupted.",
        )

    # --- Run the full diagnosis pipeline ---
    try:
        result = await _diagnosis_service.run(
            image_base64=processed["base64"],
            image_bytes=image_bytes,
            request_id=request_id,
        )
    except Exception as e:
        logger.error(f"[{request_id}] Diagnosis pipeline failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="AI analysis pipeline encountered an error. Please try again.",
        )

    logger.info(
        f"[{request_id}] Diagnosis complete | Disease: {result.get('disease_name')} "
        f"| Source: {result.get('source')} | Confidence: {result.get('confidence')}%"
    )

    return JSONResponse(
        status_code=200,
        content={
            "success": True,
            "request_id": request_id,
            "data": result,
        },
    )
