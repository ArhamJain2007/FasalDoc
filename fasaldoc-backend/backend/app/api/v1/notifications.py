"""
Notifications endpoint: register FCM device token for push alerts.
"""
import structlog
from fastapi import APIRouter, Depends, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_current_user, get_db
from app.models.fcm_token import FCMToken
from app.models.user import User
from app.schemas.history import RegisterTokenRequest, RegisterTokenResponse

logger = structlog.get_logger()
router = APIRouter(tags=["notifications"])


@router.post(
    "/register-token",
    response_model=RegisterTokenResponse,
    status_code=status.HTTP_200_OK,
    summary="Register FCM device token for push notifications",
)
async def register_fcm_token(
    body: RegisterTokenRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> RegisterTokenResponse:
    """
    Register or update an FCM device token for the authenticated user.
    Existing tokens are upserted by token value to prevent duplicates.

    Args:
        body: RegisterTokenRequest with FCM token string and platform.
        current_user: Authenticated user.
        db: Async DB session.
    Returns:
        RegisterTokenResponse confirming registration.
    Side effects:
        Inserts or updates a row in the fcm_tokens table.
    """
    result = await db.execute(
        select(FCMToken).where(FCMToken.token == body.token)
    )
    existing = result.scalars().first()

    if existing:
        # Update region if user has moved
        existing.region = current_user.region
        existing.platform = body.platform
        await db.commit()
        logger.info("fcm_token_updated", user_id=str(current_user.id))
    else:
        token_record = FCMToken(
            user_id=current_user.id,
            token=body.token,
            region=current_user.region,
            platform=body.platform,
        )
        db.add(token_record)
        await db.commit()
        logger.info("fcm_token_registered", user_id=str(current_user.id), platform=body.platform)

    return RegisterTokenResponse(message="Device token registered successfully.")
