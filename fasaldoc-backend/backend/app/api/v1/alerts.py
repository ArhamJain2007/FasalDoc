"""
Alerts endpoint: GET /api/v1/alerts
Returns weather-based disease risk alerts for a region.
"""
import structlog
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
import redis.asyncio as aioredis

from app.config import settings
from app.dependencies import get_current_user, get_db
from app.models.user import User
from app.schemas.history import AlertListResponse
from app.services.alert_service import AlertService

logger = structlog.get_logger()
router = APIRouter(tags=["alerts"])


async def get_redis():
    client = aioredis.from_url(settings.REDIS_URL, decode_responses=True)
    try:
        yield client
    finally:
        await client.aclose()


@router.get(
    "/alerts",
    response_model=AlertListResponse,
    summary="Get disease risk alerts for a region",
)
async def get_alerts(
    region: str = Query(..., description="Indian region name, e.g. 'Punjab'"),
    language: str = Query(default="en", pattern="^(en|hi|pa)$"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    redis_client=Depends(get_redis),
) -> AlertListResponse:
    """
    Return active disease risk alerts for the given region.
    Computed from current weather data and disease-weather correlations.
    Weather data is cached in Redis for 1 hour.

    Args:
        region: Indian state/region name.
        language: Response language code.
        current_user: Authenticated user.
        db: Async DB session.
        redis_client: Async Redis client.
    Returns:
        AlertListResponse with list of active alerts.
    """
    alert_svc = AlertService(redis_client=redis_client)
    alerts = await alert_svc.get_active_alerts(
        region=region,
        language=language,
        db=db,
    )
    return AlertListResponse(alerts=alerts, region=region)
