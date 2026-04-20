"""
Celery async tasks for processing large offline sync batches.
Used when the mobile client submits hundreds of records at once.
"""
import asyncio
import structlog
from uuid import UUID

from app.tasks.celery_app import celery_app

logger = structlog.get_logger()


@celery_app.task(
    bind=True,
    max_retries=3,
    default_retry_delay=30,
    name="app.tasks.sync_tasks.process_sync_batch",
)
def process_sync_batch(self, user_id_str: str, records_data: list[dict]) -> dict:
    """
    Process a large batch of offline scan records asynchronously.
    Used as a fallback when a sync payload exceeds real-time processing capacity.
    Idempotent: duplicate record IDs are safely skipped.

    Args:
        user_id_str: String UUID of the user who submitted the batch.
        records_data: List of serialized ScanRecord dicts.
    Returns:
        Dict with synced_count, skipped_count.
    Side effects:
        Inserts new Scan rows into the database.
    """
    from app.services.sync_service import SyncService
    from app.schemas.history import ScanRecord
    from app.db.session import AsyncSessionLocal

    async def _process():
        user_id = UUID(user_id_str)
        records = [ScanRecord(**r) for r in records_data]
        sync_svc = SyncService()

        async with AsyncSessionLocal() as db:
            synced, skipped = await sync_svc.sync_records(records, user_id, db)

        return {"synced_count": len(synced), "skipped_count": len(skipped)}

    try:
        result = asyncio.run(_process())
        logger.info("sync_batch_complete", user_id=user_id_str, **result)
        return result
    except Exception as exc:
        logger.error("sync_batch_failed", user_id=user_id_str, error=str(exc))
        raise self.retry(exc=exc)
