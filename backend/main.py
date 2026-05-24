"""
AgriSense Backend - Main Application Entry Point
FastAPI application with full CORS support, structured routing, and lifecycle management.
"""

import logging
import os
from contextlib import asynccontextmanager

import uvicorn
from dotenv import load_dotenv

# Load environment variables early so all services can access them
load_dotenv(override=True)

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from api.routes import advisory, analyze, chat, health

# ---------------------------------------------------------------------------
# Logging configuration
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S",
)
logger = logging.getLogger("agrisense.main")


# ---------------------------------------------------------------------------
# Application lifespan (startup / shutdown hooks)
# ---------------------------------------------------------------------------
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage startup and shutdown events."""
    logger.info("🌱 AgriSense backend starting up...")

    # Validate required environment variables on startup
    required_vars = ["LLAMA_API_KEY", "QWEN_API_KEY", "CONSENSUS_API_KEY"]
    missing = [v for v in required_vars if not os.getenv(v)]
    if missing:
        logger.warning(
            f"⚠️  Missing environment variables: {', '.join(missing)}. "
            "Some services may not function correctly."
        )

    # Ensure the uploads directory exists
    os.makedirs("uploads", exist_ok=True)
    logger.info("✅ Startup complete. AgriSense is ready.")

    yield

    logger.info("🛑 AgriSense backend shutting down...")


# ---------------------------------------------------------------------------
# FastAPI application instance
# ---------------------------------------------------------------------------
app = FastAPI(
    title="AgriSense AI Backend",
    description=(
        "AI-powered crop disease detection platform using dual Vision Language Models "
        "(Llama + Qwen) with consensus validation and an agricultural chatbot."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# ---------------------------------------------------------------------------
# CORS Middleware — allow the Next.js frontend origin
# ---------------------------------------------------------------------------
origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Global exception handler — return clean JSON for unhandled errors
# ---------------------------------------------------------------------------
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled error on {request.method} {request.url}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": "An internal server error occurred. Please try again.",
            "detail": str(exc),
        },
    )


# ---------------------------------------------------------------------------
# Register API routers
# ---------------------------------------------------------------------------
app.include_router(health.router, tags=["Health"])
app.include_router(analyze.router, prefix="/analyze", tags=["Disease Analysis"])
app.include_router(chat.router, prefix="/chat", tags=["Agricultural Chatbot"])
app.include_router(advisory.router, prefix="/advisory", tags=["Weather Advisory"])


# ---------------------------------------------------------------------------
# Root redirect info
# ---------------------------------------------------------------------------
@app.get("/", include_in_schema=False)
async def root():
    return {
        "service": "AgriSense AI Backend",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health",
    }


# ---------------------------------------------------------------------------
# Run directly with: python main.py
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=os.getenv("HOST", "0.0.0.0"),
        port=int(os.getenv("PORT", 8000)),
        reload=os.getenv("ENV", "development") == "development",
        log_level="info",
    )
