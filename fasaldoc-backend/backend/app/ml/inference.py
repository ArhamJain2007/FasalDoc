"""
End-to-end inference pipeline: image bytes → prediction result.
"""
import asyncio
import structlog
from concurrent.futures import ThreadPoolExecutor
from PIL import Image
import io
import numpy as np

from app.ml.model import ModelLoader
from app.ml.preprocessing import preprocess_image
from app.ml.postprocessing import decode_predictions, PredictionResult
from app.core.exceptions import InferenceError

logger = structlog.get_logger()

# Thread pool for running CPU-bound inference without blocking the event loop
_executor = ThreadPoolExecutor(max_workers=4)


def _run_inference_sync(image_bytes: bytes) -> PredictionResult:
    """
    Synchronous inference: decode → preprocess → infer → postprocess.
    Runs in a thread pool to avoid blocking the async event loop.

    Args:
        image_bytes: Raw bytes of a JPEG/PNG/WebP image.
    Returns:
        PredictionResult with disease metadata and confidence.
    Raises:
        InferenceError: If model inference fails unexpectedly.
        LowConfidenceError: If confidence is below threshold.
        ValueError: If image cannot be decoded.
    """
    # 1. Decode bytes to PIL Image
    try:
        image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    except Exception as exc:
        raise ValueError(f"Cannot decode image bytes: {exc}") from exc

    # 2. Preprocess
    tensor = preprocess_image(image)

    # 3. Run inference
    try:
        model = ModelLoader.get()

        if ModelLoader.is_tflite():
            # TFLite path
            input_details = model.get_input_details()
            output_details = model.get_output_details()

            # Handle INT8 quantized models
            input_dtype = input_details[0]["dtype"]
            if input_dtype == np.int8:
                scale, zero_point = input_details[0]["quantization"]
                tensor_quantized = (tensor / scale + zero_point).astype(np.int8)
                model.set_tensor(input_details[0]["index"], tensor_quantized)
            else:
                model.set_tensor(input_details[0]["index"], tensor)

            model.invoke()
            raw_output = model.get_tensor(output_details[0]["index"])[0]

            # Dequantize if output is INT8
            output_dtype = output_details[0]["dtype"]
            if output_dtype == np.int8:
                out_scale, out_zero_point = output_details[0]["quantization"]
                predictions = (raw_output.astype(np.float32) - out_zero_point) * out_scale
            else:
                predictions = raw_output.astype(np.float32)
        else:
            # Keras path
            predictions = model.predict(tensor, verbose=0)[0]

    except Exception as exc:
        logger.error("Model inference failed", error=str(exc))
        raise InferenceError(f"Model inference failed: {exc}") from exc

    # 4. Postprocess
    return decode_predictions(predictions)


async def predict(image_bytes: bytes) -> PredictionResult:
    """
    Async entry point for the inference pipeline.
    Offloads CPU-bound inference to a thread pool executor.

    Args:
        image_bytes: Raw bytes of a JPEG/PNG/WebP image (already validated).
    Returns:
        PredictionResult with disease_name, confidence, crop_name, stage, etc.
    Raises:
        InferenceError: If model inference fails unexpectedly.
        LowConfidenceError: If confidence is below threshold.
        ValueError: If image cannot be decoded.
    """
    loop = asyncio.get_event_loop()
    result = await loop.run_in_executor(_executor, _run_inference_sync, image_bytes)
    logger.info(
        "inference_complete",
        disease=result.disease_name,
        crop=result.crop_name,
        confidence=result.confidence,
        stage=result.stage,
    )
    return result
