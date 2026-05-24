"""
utils/validators.py — Input validation for uploaded images and API requests.
"""

import os
import logging

logger = logging.getLogger("agrisense.utils.validators")

# Supported MIME types and their corresponding magic byte signatures
ALLOWED_MIME_TYPES = {"image/jpeg", "image/jpg", "image/png", "image/webp"}
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}

# Magic bytes (file signatures) for format verification
MAGIC_BYTES: dict[bytes, str] = {
    b"\xff\xd8\xff": "image/jpeg",
    b"\x89PNG\r\n\x1a\n": "image/png",
    b"RIFF": "image/webp",  # WebP starts with RIFF....WEBP
}

def validate_image_upload(
    image_bytes: bytes,
    content_type: str | None,
    filename: str | None,
) -> None:
    """
    Validate that an uploaded file is a supported, non-corrupted image.

    Checks:
    1. Non-empty file
    2. File extension is allowed
    3. MIME type is in the allowed list
    4. Magic bytes confirm the actual format
    5. File size does not exceed MAX_IMAGE_SIZE_MB

    Raises:
        ValueError: With a descriptive message if validation fails.
    """
    max_size_mb = float(os.getenv("MAX_IMAGE_SIZE_MB", 10))
    max_size_bytes = int(max_size_mb * 1024 * 1024)

    # 1. Non-empty check
    if not image_bytes:
        raise ValueError("Uploaded file is empty. Please select a valid image.")

    # 2. File size check
    size_mb = len(image_bytes) / (1024 * 1024)
    if len(image_bytes) > max_size_bytes:
        raise ValueError(
            f"Image size ({size_mb:.1f} MB) exceeds the maximum allowed size of {max_size_mb} MB."
        )

    # 3. File extension check
    if filename:
        ext = os.path.splitext(filename.lower())[1]
        if ext not in ALLOWED_EXTENSIONS:
            raise ValueError(
                f"File extension '{ext}' is not supported. "
                f"Allowed formats: {', '.join(ALLOWED_EXTENSIONS)}"
            )

    # 4. MIME type check
    if content_type and content_type.lower() not in ALLOWED_MIME_TYPES:
        raise ValueError(
            f"Content type '{content_type}' is not supported. "
            f"Allowed types: {', '.join(ALLOWED_MIME_TYPES)}"
        )

    # 5. Magic bytes verification (guards against MIME type spoofing)
    _verify_magic_bytes(image_bytes)

    logger.debug(f"Image validated successfully: {filename} ({size_mb:.2f} MB)")


def _verify_magic_bytes(data: bytes) -> None:
    """Verify file format using magic byte signatures."""
    for magic, fmt in MAGIC_BYTES.items():
        if data[:len(magic)] == magic:
            # Extra WebP check — bytes 8-12 must be "WEBP"
            if fmt == "image/webp" and data[8:12] != b"WEBP":
                continue
            return  # Valid format

    raise ValueError(
        "File content does not match a supported image format (JPEG, PNG, or WebP). "
        "The file may be corrupted or renamed."
    )
