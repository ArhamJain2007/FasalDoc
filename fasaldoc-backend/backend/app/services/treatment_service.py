"""
Treatment service: fetch disease and treatment information with Redis caching.
"""
import json
import structlog
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.disease import Disease
from app.models.treatment import Treatment
from app.schemas.history import TreatmentResponse, TreatmentItem

logger = structlog.get_logger()

# Redis TTL for treatment lookups: 24 hours
TREATMENT_CACHE_TTL = 86400


class TreatmentService:
    """
    Fetches treatment plans for a given disease ID.
    Results are cached in Redis for 24 hours to minimize DB load.
    """

    def __init__(self, redis_client) -> None:
        self._redis = redis_client

    async def get_treatment(
        self,
        disease_id: str,
        language: str,
        db: AsyncSession,
    ) -> TreatmentResponse | None:
        """
        Fetch treatment plan for a disease, using Redis cache.

        Args:
            disease_id: The disease identifier (e.g. "tomato_early_blight").
            language: ISO 639-1 language code ("en", "hi", "pa").
            db: Async DB session.
        Returns:
            TreatmentResponse with localized disease info and treatment items,
            or None if disease_id not found.
        Side effects:
            Caches result in Redis with 24-hour TTL on first fetch.
        """
        cache_key = f"treatment:{disease_id}:{language}"

        # Check Redis cache
        cached = await self._redis.get(cache_key)
        if cached:
            logger.debug("treatment_cache_hit", disease_id=disease_id, lang=language)
            return TreatmentResponse.model_validate_json(cached)

        # Query DB
        disease_result = await db.execute(
            select(Disease).where(Disease.id == disease_id)
        )
        disease = disease_result.scalars().first()
        if disease is None:
            return None

        treatments_result = await db.execute(
            select(Treatment).where(Treatment.disease_id == disease_id)
        )
        treatments = treatments_result.scalars().all()

        # Localize
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

        treatment_items: list[TreatmentItem] = []
        for t in treatments:
            if language == "hi":
                name = t.name_hi
            elif language == "pa":
                name = t.name_pa
            else:
                name = t.name_en

            treatment_items.append(
                TreatmentItem(
                    treatment_id=str(t.id),
                    type=t.type,
                    name=name,
                    dosage=t.dosage,
                    schedule=t.schedule,
                )
            )

        response = TreatmentResponse(
            disease_id=disease_id,
            disease_name=disease_name,
            crop_name=crop_name,
            description=description,
            severity=disease.severity,
            treatments=treatment_items,
        )

        # Store in Redis
        await self._redis.setex(
            cache_key,
            TREATMENT_CACHE_TTL,
            response.model_dump_json(),
        )
        logger.debug("treatment_cache_set", disease_id=disease_id, lang=language)
        return response
