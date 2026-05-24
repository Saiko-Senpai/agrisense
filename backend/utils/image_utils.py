"""
utils/image_utils.py — Async image preprocessing and base64 encoding utilities.

Handles:
- Image validation (format, size)
- Resizing to max dimensions
- JPEG compression to reduce API payload size
- Base64 encoding for multimodal API calls
"""

import asyncio
import base64
import io
import logging
from typing import Any

from PIL import Image, UnidentifiedImageError

logger = logging.getLogger("agrisense.utils.image")

# Processing configuration
MAX_WIDTH = 1024
MAX_HEIGHT = 1024
JPEG_QUALITY = 85  # Compress to reduce payload size while retaining clarity


class ImageProcessor:
    """Async-compatible image preprocessing pipeline."""

    async def preprocess(self, image_bytes: bytes) -> dict[str, Any]:
        """
        Preprocess raw image bytes into a normalized, compressed form.

        Returns:
            dict with keys:
              - "base64": base64-encoded string (no data URI prefix)
              - "mime_type": "image/jpeg"
              - "width": processed width
              - "height": processed height
              - "size_kb": processed file size in KB
        """
        # Offload CPU-bound PIL work to a thread pool
        return await asyncio.get_event_loop().run_in_executor(
            None, self._process_sync, image_bytes
        )

    def _process_sync(self, image_bytes: bytes) -> dict[str, Any]:
        """Synchronous image processing logic."""
        try:
            img = Image.open(io.BytesIO(image_bytes))
        except UnidentifiedImageError:
            raise ValueError("Cannot open image — file may be corrupted or unsupported.")

        # Convert to RGB to handle PNG transparency, RGBA, palette modes, etc.
        if img.mode not in ("RGB",):
            img = img.convert("RGB")

        # Resize if larger than max dimensions (preserve aspect ratio)
        if img.width > MAX_WIDTH or img.height > MAX_HEIGHT:
            img.thumbnail((MAX_WIDTH, MAX_HEIGHT), Image.LANCZOS)
            logger.debug(f"Resized image to {img.size}")

        # Encode to JPEG buffer
        buffer = io.BytesIO()
        img.save(buffer, format="JPEG", quality=JPEG_QUALITY, optimize=True)
        buffer.seek(0)
        jpeg_bytes = buffer.read()

        # Base64 encode
        encoded = base64.b64encode(jpeg_bytes).decode("utf-8")

        return {
            "base64": encoded,
            "mime_type": "image/jpeg",
            "width": img.width,
            "height": img.height,
            "size_kb": round(len(jpeg_bytes) / 1024, 1),
        }


def bytes_to_base64(data: bytes) -> str:
    """Convert raw bytes to a base64-encoded string."""
    return base64.b64encode(data).decode("utf-8")


def base64_to_bytes(encoded: str) -> bytes:
    """Convert a base64-encoded string back to raw bytes."""
    return base64.b64decode(encoded)
