"""Extract text from images using OCR."""

from __future__ import annotations

import base64
import mimetypes
from pathlib import Path

# We'll use Anthropic API for vision instead of OpenAI
# This will be integrated in extraction layer


def image_to_base64(image_path: Path) -> tuple[str, str]:
    """Convert image to base64 string with MIME type.
    
    Args:
        image_path: Path to image file
        
    Returns:
        Tuple of (mime_type, base64_string)
    """
    image_path = image_path.expanduser().resolve()
    if not image_path.exists():
        raise FileNotFoundError(f"Image file not found: {image_path}")
    
    # Detect MIME type
    mime_type, _ = mimetypes.guess_type(str(image_path))
    if mime_type is None:
        mime_type = "image/png"
    
    # Read and encode
    encoded = base64.b64encode(image_path.read_bytes()).decode("utf-8")
    
    return mime_type, encoded


def read_image_as_data_url(image_path: Path) -> str:
    """Convert image to data URL format for API calls.
    
    Args:
        image_path: Path to image file
        
    Returns:
        Data URL string (data:image/png;base64,...)
    """
    mime_type, b64_data = image_to_base64(image_path)
    return f"data:{mime_type};base64,{b64_data}"