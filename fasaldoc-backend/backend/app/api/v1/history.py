"""
Scan history endpoints: list, retrieve, and update user scan records.
"""
from uuid import UUID

import structlog
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_current_user, get_db
from app.models.scan import Scan
from app.models.user import User
from app.schemas.history import (
    ScanHistoryResponse,
    ScanHistoryItem,
    ScanDetailResponse,
    UpdateScanStatusRequest,
)

logger = structlog.get_logger()
router = APIRouter(tags=["history"])


@router.get(
    "/history",
    response_model=ScanHistoryResponse,
    summary="Get paginated scan history for the current user",
)
async def get_history(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    crop: str | None = Query(default=None, description="Filter by crop name"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ScanHistoryResponse:
    """
    Return paginated list of scan records for the authenticated user,
    ordered by most recent first.

    Args:
        page: Page number (1-indexed).
        page_size: Records per page (max 100).
        crop: Optional crop name filter.
        current_user: Authenticated user.
        db: Async DB session.
    Returns:
        ScanHistoryResponse with items, total, page, and page_size.
    """
    query = select(Scan).where(Scan.user_id == current_user.id)
    if crop:
        query = query.where(Scan.crop_name.ilike(f"%{crop}%"))

    count_result = await db.execute(
        select(func.count()).select_from(query.subquery())
    )
    total = count_result.scalar_one()

    query = query.order_by(Scan.created_at.desc())
    query = query.offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(query)
    scans = result.scalars().all()

    items = [
        ScanHistoryItem(
            scan_id=str(s.id),
            disease_name=s.disease_name,
            crop_name=s.crop_name,
            confidence=s.confidence,
            stage=s.stage,
            image_url=s.image_url,
            status=s.status,
            treatment_id=s.treatment_id,
            scan_date=s.created_at.isoformat(),
        )
        for s in scans
    ]

    return ScanHistoryResponse(items=items, total=total, page=page, page_size=page_size)


@router.get(
    "/history/{scan_id}",
    response_model=ScanDetailResponse,
    summary="Get a single scan record by ID",
)
async def get_scan(
    scan_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ScanDetailResponse:
    """
    Retrieve a single scan record by UUID.
    Returns 403 if the scan belongs to a different user.

    Args:
        scan_id: UUID string of the scan.
        current_user: Authenticated user.
        db: Async DB session.
    Returns:
        ScanDetailResponse with full scan details.
    Raises:
        404: Scan not found.
        403: Scan belongs to another user.
    """
    try:
        scan_uuid = UUID(scan_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": "NOT_FOUND", "message": f"Scan {scan_id} not found.", "detail": {}},
        )

    result = await db.execute(select(Scan).where(Scan.id == scan_uuid))
    scan = result.scalars().first()

    if not scan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": "NOT_FOUND", "message": f"Scan {scan_id} not found.", "detail": {}},
        )
    if scan.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"error": "FORBIDDEN", "message": "You do not have access to this scan.", "detail": {}},
        )

    return ScanDetailResponse(
        scan_id=str(scan.id),
        disease_name=scan.disease_name,
        crop_name=scan.crop_name,
        confidence=scan.confidence,
        stage=scan.stage,
        image_url=scan.image_url,
        status=scan.status,
        treatment_id=scan.treatment_id,
        scan_date=scan.created_at.isoformat(),
        synced_from_offline=scan.synced_from_offline,
    )


@router.patch(
    "/history/{scan_id}",
    response_model=ScanDetailResponse,
    summary="Update scan treatment status",
)
async def update_scan_status(
    scan_id: str,
    body: UpdateScanStatusRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ScanDetailResponse:
    """
    Update the treatment status of a scan (active → treated → resolved).

    Args:
        scan_id: UUID string of the scan to update.
        body: UpdateScanStatusRequest with new status.
        current_user: Authenticated user.
        db: Async DB session.
    Returns:
        Updated ScanDetailResponse.
    Raises:
        404: Scan not found.
        403: Scan belongs to another user.
    """
    try:
        scan_uuid = UUID(scan_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": "NOT_FOUND", "message": f"Scan {scan_id} not found.", "detail": {}},
        )

    result = await db.execute(select(Scan).where(Scan.id == scan_uuid))
    scan = result.scalars().first()

    if not scan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": "NOT_FOUND", "message": f"Scan {scan_id} not found.", "detail": {}},
        )
    if scan.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"error": "FORBIDDEN", "message": "You do not have access to this scan.", "detail": {}},
        )

    scan.status = body.status
    await db.commit()
    await db.refresh(scan)

    return ScanDetailResponse(
        scan_id=str(scan.id),
        disease_name=scan.disease_name,
        crop_name=scan.crop_name,
        confidence=scan.confidence,
        stage=scan.stage,
        image_url=scan.image_url,
        status=scan.status,
        treatment_id=scan.treatment_id,
        scan_date=scan.created_at.isoformat(),
        synced_from_offline=scan.synced_from_offline,
    )
