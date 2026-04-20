"""
Postprocessing: decode raw model output tensor into structured prediction result.
"""
import numpy as np
from dataclasses import dataclass
from app.ml.classes import PLANT_DISEASE_CLASSES, CLASS_TO_DISEASE_ID, DISEASE_DISPLAY
from app.config import settings
from app.core.exceptions import LowConfidenceError


@dataclass
class PredictionResult:
    disease_name: str
    crop_name: str
    disease_name_hi: str
    crop_name_hi: str
    disease_name_pa: str
    crop_name_pa: str
    confidence: float
    class_index: int
    class_label: str
    disease_id: str
    stage: str
    all_probs: dict[str, float]


def parse_label(label: str) -> tuple[str, str]:
    """
    Parse a PlantVillage label string into (crop_name, disease_name).

    Args:
        label: Label like "Tomato___Early_blight".
    Returns:
        Tuple of (crop_name, disease_name) as readable strings.
    """
    parts = label.split("___")
    crop = parts[0].replace("_", " ")
    disease = parts[1].replace("_", " ") if len(parts) > 1 else "Unknown"
    return crop, disease


def compute_stage(confidence: float) -> str:
    """
    Map model confidence to disease severity stage.
    Used as a proxy until a dedicated stage-prediction model is trained.

    Args:
        confidence: Prediction confidence as percentage (0-100).
    Returns:
        Stage string: "Stage 1", "Stage 2", or "Stage 3".
    """
    if confidence >= 85:
        return "Stage 3"
    if confidence >= 70:
        return "Stage 2"
    return "Stage 1"


def decode_predictions(predictions: np.ndarray) -> PredictionResult:
    """
    Map softmax output tensor to a structured PredictionResult.

    Args:
        predictions: np.ndarray of shape (38,) — softmax probabilities.
    Returns:
        PredictionResult with disease metadata.
    Raises:
        LowConfidenceError: If max confidence is below CONFIDENCE_THRESHOLD.
        IndexError: If class index is outside expected range.
    """
    top_idx = int(np.argmax(predictions))
    confidence = float(predictions[top_idx]) * 100.0

    if confidence < settings.CONFIDENCE_THRESHOLD * 100:
        raise LowConfidenceError(
            f"Confidence {confidence:.1f}% is below threshold "
            f"{settings.CONFIDENCE_THRESHOLD * 100:.0f}%. "
            "Image may be unclear or not a plant leaf."
        )

    if top_idx >= len(PLANT_DISEASE_CLASSES):
        raise IndexError(
            f"Class index {top_idx} out of range for "
            f"{len(PLANT_DISEASE_CLASSES)} classes"
        )

    class_label = PLANT_DISEASE_CLASSES[top_idx]
    display = DISEASE_DISPLAY.get(class_label, {})
    disease_id = CLASS_TO_DISEASE_ID.get(class_label, class_label.lower().replace("___", "_"))

    crop_name, disease_name = parse_label(class_label)

    return PredictionResult(
        disease_name=display.get("disease_name", disease_name),
        crop_name=display.get("crop_name", crop_name),
        disease_name_hi=display.get("disease_name_hi", disease_name),
        crop_name_hi=display.get("crop_name_hi", crop_name),
        disease_name_pa=display.get("disease_name_pa", disease_name),
        crop_name_pa=display.get("crop_name_pa", crop_name),
        confidence=round(confidence, 1),
        class_index=top_idx,
        class_label=class_label,
        disease_id=disease_id,
        stage=compute_stage(confidence),
        all_probs={
            PLANT_DISEASE_CLASSES[i]: round(float(p) * 100, 2)
            for i, p in enumerate(predictions)
        },
    )
