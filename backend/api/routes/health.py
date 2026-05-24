"""
GET /health — Liveness and readiness health check endpoint.
"""

import os
import time

from fastapi import APIRouter
from fastapi.responses import JSONResponse

router = APIRouter()

# Track server start time for uptime reporting
_start_time = time.time()


@router.get("/health", summary="Health check", response_description="Service health status")
async def health_check() -> JSONResponse:
    """
    Returns the current health and status of the AgriSense backend.

    Checks:
    - API key availability (without exposing values)
    - Service uptime
    """
    uptime_seconds = round(time.time() - _start_time, 1)

    services = {
        "llama": bool(os.getenv("LLAMA_API_KEY")),
        "qwen": bool(os.getenv("QWEN_API_KEY")),
        "consensus": bool(os.getenv("CONSENSUS_API_KEY")),
    }

    all_healthy = all(services.values())

    return JSONResponse(
        status_code=200 if all_healthy else 206,
        content={
            "success": True,
            "status": "healthy" if all_healthy else "degraded",
            "uptime_seconds": uptime_seconds,
            "version": "1.0.0",
            "services": {k: "configured" if v else "missing_key" for k, v in services.items()},
        },
    )
