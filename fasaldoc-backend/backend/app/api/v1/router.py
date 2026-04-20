"""
API v1 router: aggregates all endpoint routers under /api/v1.
"""
from fastapi import APIRouter

from app.api.v1 import auth, detect, history, alerts, treatment, sync, notifications

api_router = APIRouter()

api_router.include_router(auth.router)
api_router.include_router(detect.router)
api_router.include_router(history.router)
api_router.include_router(alerts.router)
api_router.include_router(treatment.router)
api_router.include_router(sync.router)
api_router.include_router(notifications.router)
