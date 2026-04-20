"""
Sync endpoint: POST /api/v1/sync
Accepts batch of offline scan records from mobile client and upserts them.
"""
import structlog
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_current_user, get_db
from app.models.user import User
from app.schemas.history import SyncRequest, SyncResponse
from app.services.sync_service import SyncService

logger = structlog.get_logger()
router = APIRouter(tags=["sync"])


@router.post(
    "/sync",
    response_model=SyncResponse,
    status_code=status.HTTP_200_OK,
    summary="Batch sync offline scan records",
)
async def sync_offline_records(
    body: SyncRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> SyncResponse:
    """
    Accept up to 200 offline scan records from the mobile app and persist them.
    Idempotent: records that already exist are acknowledged without duplication.

    Args:
        body: SyncRequest with list of ScanRecord objects (max 200).
        current_user: Authenticated user.
        db: Async DB session.
    Returns:
        SyncResponse with synced IDs, skipped IDs, and totals.
    """
    sync_svc = SyncService()
    synced_ids, skipped_ids = await sync_svc.sync_records(
        records=body.records,
        user_id=current_user.id,
        db=db,
    )

    return SyncResponse(
        synced=synced_ids,
        skipped=skipped_ids,
        total_received=len(body.records),
        total_synced=len(synced_ids),
    )
