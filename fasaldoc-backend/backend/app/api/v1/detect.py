"""
Disease detection endpoint.
Accepts a plant leaf image, runs ML inference, returns diagnosis + treatment reference.
"""
from uuid import uuid4

import structlog
from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.core.exceptions import InferenceError, LowConfidenceError
from app.dependencies import get_current_user, get_db
from app.ml.model import ModelLoader
from app.models.user import User
from app.schemas.detect import DetectionResponse
from app.services.detection_service import DetectionService
from app.services.storage_service import StorageService

logger = structlog.get_logger()
router = APIRouter(tags=["detection"])

ALLOWED_CONTENT_TYPES = {"image/jpeg", "image/png", "image/webp"}
MAX_IMAGE_BYTES = 10 * 1024 * 1024  # 10 MB


def _stage_to_severity(stage: str) -> str:
    """Map Stage 1/2/3 to low/medium/high for frontend compatibility."""
    if stage == "Stage 3":
        return "high"
    if stage == "Stage 2":
        return "medium"
    return "low"


@router.post(
    "/detect",
    response_model=DetectionResponse,
    status_code=status.HTTP_200_OK,
    summary="Detect plant disease from leaf image",
)
async def detect_disease(
    file: UploadFile = File(..., description="Plant leaf image (JPEG/PNG/WebP, max 10MB)"),
    language: str = Query(default="en", pattern="^(en|hi|pa)$", description="Response language"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> DetectionResponse:
    """
    Full detection pipeline:
    1. Validate file type and size.
    2. Upload original image to S3.
    3. Run EfficientNetB4 inference.
    4. Enrich with localized disease metadata + treatment ID.
    5. Persist scan record to DB.
    6. Return result including severity field for frontend compatibility.
    """
    # Guard: model must be loaded
    if not ModelLoader.is_loaded():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "error": "MODEL_NOT_LOADED",
                "message": "ML model is still loading. Please retry in a few seconds.",
                "detail": {},
            },
        )

    # Validate content type
    if file.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": "INVALID_FILE_TYPE",
                "message": f"Only JPEG, PNG, and WebP images are accepted. Got: {file.content_type}",
                "detail": {"received_content_type": file.content_type},
            },
        )

    # Read and validate size
    contents = await file.read()
    if len(contents) > MAX_IMAGE_BYTES:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail={
                "error": "FILE_TOO_LARGE",
                "message": f"Image too large. Max 10 MB. Got: {len(contents) / 1024 / 1024:.1f} MB",
                "detail": {"size_bytes": len(contents), "max_bytes": MAX_IMAGE_BYTES},
            },
        )

    # Upload to S3
    storage = StorageService()
    s3_key = f"scans/{current_user.id}/{uuid4()}.jpg"
    try:
        image_url = await storage.upload(contents, s3_key, content_type=file.content_type)
    except Exception as exc:
        logger.warning("s3_upload_failed_continuing", error=str(exc))
        image_url = f"local://{s3_key}"

    # Run ML inference
    detection_svc = DetectionService()
    try:
        result = await detection_svc.detect(contents)
    except LowConfidenceError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "error": "LOW_CONFIDENCE",
                "message": str(exc),
                "detail": {"suggestion": "Please take a clearer photo of the affected leaf."},
            },
        )
    except InferenceError as exc:
        logger.error("inference_error", user_id=str(current_user.id), error=str(exc))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "INFERENCE_ERROR", "message": "Detection failed. Please try again.", "detail": {}},
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={"error": "INVALID_IMAGE", "message": f"Cannot decode image: {exc}", "detail": {}},
        )

    # Enrich with localized names and treatment reference
    enriched = await detection_svc.enrich(result, language=language, db=db)

    # Persist scan record
    scan = await detection_svc.save_scan(
        db=db,
        user_id=current_user.id,
        result=result,
        enriched=enriched,
        image_url=image_url,
    )

    return DetectionResponse(
        scan_id=str(scan.id),
        disease_name=enriched.disease_name,
        crop_name=enriched.crop_name,
        confidence=result.confidence,
        stage=result.stage,
        treatment_id=enriched.treatment_id,
        description=enriched.description,
        image_url=image_url,
        scan_date=scan.created_at.isoformat(),
        severity=_stage_to_severity(result.stage),
    )
