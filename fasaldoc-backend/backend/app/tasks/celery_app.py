"""
Celery application instance with Redis broker and beat schedule.
"""
from celery import Celery
from celery.schedules import crontab
from app.config import settings

celery_app = Celery(
    "fasaldoc",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=[
        "app.tasks.alert_tasks",
        "app.tasks.sync_tasks",
    ],
)

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="Asia/Kolkata",
    enable_utc=True,
    task_track_started=True,
    task_acks_late=True,            # Re-queue on worker crash
    worker_prefetch_multiplier=1,   # Fair dispatch for long-running tasks
    beat_schedule={
        "check-alerts-every-6-hours": {
            "task": "app.tasks.alert_tasks.check_and_send_alerts",
            "schedule": crontab(minute=0, hour="*/6"),
        },
    },
)
