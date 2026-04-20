"""
Celery beat tasks: periodic weather checks and regional alert broadcasts.
All tasks are idempotent — safe to retry without side-effect duplication.
"""
import asyncio
import structlog
import redis as redis_sync

from app.tasks.celery_app import celery_app
from app.config import settings

logger = structlog.get_logger()

REGIONS = [
    "Punjab",
    "Haryana",
    "Uttar Pradesh",
    "Madhya Pradesh",
    "Maharashtra",
    "Delhi",
    "Rajasthan",
    "Bihar",
    "West Bengal",
    "Karnataka",
    "Tamil Nadu",
    "Andhra Pradesh",
    "Gujarat",
]


def _get_redis():
    return redis_sync.from_url(settings.REDIS_URL, decode_responses=True)


@celery_app.task(
    bind=True,
    max_retries=3,
    default_retry_delay=60,
    name="app.tasks.alert_tasks.check_and_send_alerts",
)
def check_and_send_alerts(self) -> dict:
    """
    Scheduled task: runs every 6 hours via Celery Beat.
    For each major Indian agricultural region:
      1. Fetch weather data from OpenWeatherMap.
      2. Evaluate disease-weather rules.
      3. Send FCM push notifications to at-risk users in danger zones.

    Returns:
        Dict summarising regions processed and alerts dispatched.
    Side effects:
        Sends FCM push notifications; writes Alert records to DB.
    """
    from app.services.alert_service import AlertService
    from app.services.notification_service import NotificationService
    from app.db.session import AsyncSessionLocal
    from app.models.fcm_token import FCMToken
    from sqlalchemy import select

    NotificationService.init()
    redis_client = _get_redis()

    results = {"regions_processed": 0, "alerts_dispatched": 0, "errors": []}

    async def _process():
        async with AsyncSessionLocal() as db:
            alert_svc = AlertService(redis_client=redis_client)
            notif_svc = NotificationService()

            for region in REGIONS:
                try:
                    alerts = await alert_svc.compute_alerts(region, "hi", db)
                    results["regions_processed"] += 1

                    danger_alerts = [a for a in alerts if a.alert_type == "danger"]
                    if not danger_alerts:
                        continue

                    # Fetch all FCM tokens for the region
                    token_result = await db.execute(
                        select(FCMToken.token).where(FCMToken.region == region)
                    )
                    tokens = [row[0] for row in token_result.fetchall()]

                    if not tokens:
                        continue

                    for alert in danger_alerts:
                        sent = await notif_svc.broadcast_region(
                            tokens=tokens,
                            title=alert.title,
                            body=alert.body,
                        )
                        results["alerts_dispatched"] += sent
                        logger.info(
                            "alert_broadcast",
                            region=region,
                            disease=alert.related_disease_id,
                            tokens_sent=sent,
                        )

                except Exception as exc:
                    logger.error("region_alert_failed", region=region, error=str(exc))
                    results["errors"].append({"region": region, "error": str(exc)})

    try:
        asyncio.run(_process())
    except Exception as exc:
        logger.error("check_and_send_alerts_failed", error=str(exc))
        raise self.retry(exc=exc)

    logger.info("check_and_send_alerts_complete", **results)
    return results
