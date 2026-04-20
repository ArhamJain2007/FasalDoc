"""
Sync service: idempotently upsert offline scan records submitted in batch.
"""
from datetime import datetime
from uuid import UUID

import structlog
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.scan import Scan
from app.schemas.history import ScanRecord

logger = structlog.get_logger()


class SyncService:
    """
    Handles batch synchronization of offline scan records from mobile clients.
    All operations are idempotent — safe to retry without creating duplicates.
    """

    async def sync_records(
        self,
        records: list[ScanRecord],
        user_id: UUID,
        db: AsyncSession,
    ) -> tuple[list[str], list[str]]:
        """
        Upsert a batch of offline scan records for the authenticated user.
        Records that already exist in the DB are acknowledged but not duplicated.

        Args:
            records: List of ScanRecord objects from the mobile client.
            user_id: UUID of the authenticated user.
            db: Async DB session.
        Returns:
            Tuple of (synced_ids, skipped_ids).
            synced_ids: IDs successfully inserted.
            skipped_ids: IDs that already existed.
        Side effects:
            Inserts new rows into the scans table.
        """
        synced_ids: list[str] = []
        skipped_ids: list[str] = []

        for record in records:
            try:
                record_uuid = UUID(record.id)
            except ValueError:
                logger.warning("sync_invalid_uuid", id=record.id)
                skipped_ids.append(record.id)
                continue

            # Check for existing record
            existing = await db.execute(
                select(Scan).where(Scan.id == record_uuid)
            )
            if existing.scalars().first() is not None:
                skipped_ids.append(record.id)
                continue

            try:
                scan_date = datetime.fromisoformat(record.scan_date)
            except (ValueError, TypeError):
                scan_date = datetime.utcnow()

            new_scan = Scan(
                id=record_uuid,
                user_id=user_id,
                disease_class_index=record.disease_class_index,
                disease_name=record.disease_name,
                crop_name=record.crop_name,
                confidence=record.confidence,
                stage=record.stage,
                image_url=record.image_uri,
                status=record.status,
                treatment_id=record.treatment_id,
                synced_from_offline=True,
                created_at=scan_date,
            )
            db.add(new_scan)
            synced_ids.append(record.id)

        if synced_ids:
            await db.commit()
            logger.info(
                "sync_complete",
                user_id=str(user_id),
                synced=len(synced_ids),
                skipped=len(skipped_ids),
            )

        return synced_ids, skipped_ids
