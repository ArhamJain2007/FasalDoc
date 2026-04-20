"""
Treatment endpoint: GET /api/v1/treatment/{disease_id}
Returns localized treatment plan for a given disease.
"""
import structlog
import redis.asyncio as aioredis
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.dependencies import get_current_user, get_db
from app.models.user import User
from app.schemas.history import TreatmentResponse
from app.services.treatment_service import TreatmentService

logger = structlog.get_logger()
router = APIRouter(tags=["treatment"])


async def get_redis():
    client = aioredis.from_url(settings.REDIS_URL, decode_responses=True)
    try:
        yield client
    finally:
        await client.aclose()


@router.get(
    "/treatment/{disease_id}",
    response_model=TreatmentResponse,
    summary="Get treatment plan for a disease",
)
async def get_treatment(
    disease_id: str,
    language: str = Query(default="en", pattern="^(en|hi|pa)$"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    redis_client=Depends(get_redis),
) -> TreatmentResponse:
    """
    Return the treatment plan (organic + chemical options) for a given disease ID.
    Results are cached in Redis for 24 hours.

    Args:
        disease_id: Disease identifier string (e.g. "tomato_early_blight").
        language: Response language code.
        current_user: Authenticated user.
        db: Async DB session.
        redis_client: Async Redis client.
    Returns:
        TreatmentResponse with localized disease info and treatment items.
    Raises:
        404: Disease ID not found.
    """
    treatment_svc = TreatmentService(redis_client=redis_client)
    result = await treatment_svc.get_treatment(
        disease_id=disease_id,
        language=language,
        db=db,
    )
    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error": "NOT_FOUND",
                "message": f"Disease '{disease_id}' not found in database.",
                "detail": {},
            },
        )
    return result
