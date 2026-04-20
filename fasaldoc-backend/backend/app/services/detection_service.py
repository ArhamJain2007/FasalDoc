"""
Detection service: orchestrates the full scan pipeline.
Calls ML inference, enriches result with DB data, and persists the scan.
"""
from uuid import UUID, uuid4
import structlog
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.ml.inference import predict
from app.ml.postprocessing import PredictionResult
from app.models.scan import Scan
from app.models.disease import Disease
from app.models.treatment import Treatment

logger = structlog.get_logger()


class EnrichedResult:
    def __init__(
        self,
        disease_name: str,
        crop_name: str,
        treatment_id: str,
        description: str,
    ) -> None:
        self.disease_name = disease_name
        self.crop_name = crop_name
        self.treatment_id = treatment_id
        self.description = description


class DetectionService:
    """
    Orchestrates disease detection:
    1. Run ML inference.
    2. Look up localized disease metadata and first treatment from DB.
    3. Persist scan record.
    """

    async def detect(self, image_bytes: bytes) -> PredictionResult:
        """
        Run ML inference on raw image bytes.

        Args:
            image_bytes: Validated image bytes (JPEG/PNG/WebP, ≤10 MB).
        Returns:
            PredictionResult with disease metadata.
        Raises:
            LowConfidenceError: If model confidence is too low.
            InferenceError: If inference fails unexpectedly.
        """
        return await predict(image_bytes)

    async def enrich(
        self,
        result: PredictionResult,
        language: str,
        db: AsyncSession,
    ) -> EnrichedResult:
        """
        Enrich a PredictionResult with localized names and treatment ID from DB.

        Args:
            result: Raw PredictionResult from ML inference.
            language: ISO 639-1 language code ("en", "hi", "pa").
            db: Async DB session for disease/treatment lookup.
        Returns:
            EnrichedResult with localized names, treatment_id, and description.
        """
        # Look up disease from DB by class index
        disease_result = await db.execute(
            select(Disease).where(Disease.class_index == result.class_index)
        )
        disease = disease_result.scalars().first()

        if disease:
            if language == "hi":
                disease_name = disease.name_hi
                crop_name = disease.crop_hi
                description = disease.description_hi
            elif language == "pa":
                disease_name = disease.name_pa
                crop_name = disease.crop_pa
                description = disease.description_pa
            else:
                disease_name = disease.name_en
                crop_name = disease.crop_en
                description = disease.description_en

            # Fetch first treatment for this disease
            treatment_result = await db.execute(
                select(Treatment).where(Treatment.disease_id == disease.id).limit(1)
            )
            treatment = treatment_result.scalars().first()
            treatment_id = str(treatment.id) if treatment else result.disease_id
        else:
            # Fallback to inference-time display names
            if language == "hi":
                disease_name = result.disease_name_hi
                crop_name = result.crop_name_hi
            elif language == "pa":
                disease_name = result.disease_name_pa
                crop_name = result.crop_name_pa
            else:
                disease_name = result.disease_name
                crop_name = result.crop_name

            description = f"{disease_name} detected on {crop_name}."
            treatment_id = result.disease_id

        return EnrichedResult(
            disease_name=disease_name,
            crop_name=crop_name,
            treatment_id=treatment_id,
            description=description,
        )

    async def save_scan(
        self,
        db: AsyncSession,
        user_id: UUID,
        result: PredictionResult,
        enriched: EnrichedResult,
        image_url: str,
    ) -> Scan:
        """
        Persist a new scan record to the database.

        Args:
            db: Async DB session.
            user_id: UUID of the authenticated user.
            result: Raw prediction result from ML inference.
            enriched: Localized result with treatment_id.
            image_url: S3 URL of the uploaded scan image.
        Returns:
            Persisted Scan ORM instance.
        Side effects:
            Inserts a row into the scans table.
        """
        scan = Scan(
            id=uuid4(),
            user_id=user_id,
            disease_class_index=result.class_index,
            disease_name=enriched.disease_name,
            crop_name=enriched.crop_name,
            confidence=result.confidence,
            stage=result.stage,
            image_url=image_url,
            status="active",
            treatment_id=enriched.treatment_id,
            synced_from_offline=False,
        )
        db.add(scan)
        await db.commit()
        await db.refresh(scan)
        logger.info(
            "scan_saved",
            scan_id=str(scan.id),
            user_id=str(user_id),
            disease=enriched.disease_name,
        )
        return scan
