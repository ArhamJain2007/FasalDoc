"""
Image preprocessing pipeline for EfficientNetB4 inference.
Matches training-time preprocessing exactly.
"""
import io
import numpy as np
from PIL import Image
from app.config import settings


def preprocess_image(image: Image.Image) -> np.ndarray:
    """
    Resize, normalize, and batch-dimension a PIL image for EfficientNetB4.

    Args:
        image: PIL Image in RGB mode.
    Returns:
        np.ndarray of shape (1, H, W, 3) with values in [-1.0, 1.0],
        dtype float32.
    """
    # Resize to model input size (224x224 default)
    image = image.resize(
        (settings.MODEL_INPUT_SIZE, settings.MODEL_INPUT_SIZE),
        Image.LANCZOS,
    )
    # Convert to numpy and normalize to [-1, 1] (EfficientNet standard)
    arr = np.array(image, dtype=np.float32)
    arr = (arr / 127.5) - 1.0
    # Add batch dimension: (1, 224, 224, 3)
    return np.expand_dims(arr, axis=0)


def preprocess_bytes(image_bytes: bytes) -> np.ndarray:
    """
    Decode raw image bytes and run preprocessing pipeline.

    Args:
        image_bytes: Raw bytes of a JPEG/PNG/WebP image.
    Returns:
        np.ndarray of shape (1, H, W, 3) ready for inference.
    Raises:
        ValueError: If image cannot be decoded.
    """
    try:
        image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    except Exception as exc:
        raise ValueError(f"Cannot decode image: {exc}") from exc
    return preprocess_image(image)
