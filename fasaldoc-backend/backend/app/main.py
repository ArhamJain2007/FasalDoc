"""
FasalDoc API — FastAPI application entry point.
Handles startup (model loading, DB seeding), middleware, routing, and exception handling.
"""
import structlog
from contextlib import asynccontextmanager

import redis.asyncio as aioredis
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from prometheus_fastapi_instrumentator import Instrumentator
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from slowapi.util import get_remote_address

from app.api.v1.router import api_router
from app.config import settings
from app.core.exceptions import (
    InferenceError,
    LowConfidenceError,
    ModelNotLoadedError,
    StorageError,
    WeatherAPIError,
)
from app.core.middleware import LoggingMiddleware
from app.db.session import engine, AsyncSessionLocal
from app.db.init_db import init_db
from app.ml.model import ModelLoader
from app.services.notification_service import NotificationService

logger = structlog.get_logger()

# Configure structlog for JSON output in production
structlog.configure(
    processors=[
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.JSONRenderer() if not settings.DEBUG else structlog.dev.ConsoleRenderer(),
    ]
)

limiter = Limiter(key_func=get_remote_address, default_limits=[f"{settings.RATE_LIMIT_PER_MINUTE}/minute"])


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager.
    Startup: load ML model, seed database, initialize Firebase.
    Shutdown: release model from memory.
    """
    logger.info("fasaldoc_startup", version="1.0.0", debug=settings.DEBUG)

    # Load ML model into memory once
    await ModelLoader.load()

    # Seed DB if empty
    async with AsyncSessionLocal() as db:
        await init_db(db)

    # Initialize Firebase Admin SDK
    NotificationService.init()

    logger.info("fasaldoc_ready")
    yield

    # Cleanup
    ModelLoader.unload()
    await engine.dispose()
    logger.info("fasaldoc_shutdown")


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.APP_NAME,
        version="1.0.0",
        description=(
            "AI-powered plant disease detection API for Indian farmers. "
            "Supports Hindi, Punjabi, and English. "
            "Provides disease diagnosis, treatment plans, and weather-based alerts."
        ),
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
        lifespan=lifespan,
    )

    # Rate limiter
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
    app.add_middleware(SlowAPIMiddleware)

    # CORS — allow React Native app origins
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Structured request logging
    app.add_middleware(LoggingMiddleware)

    # Mount API routes
    app.include_router(api_router, prefix=settings.API_V1_PREFIX)

    # Prometheus metrics at /metrics
    Instrumentator(
        should_group_status_codes=True,
        excluded_handlers=["/health", "/metrics"],
    ).instrument(app).expose(app)

    # ── Exception Handlers ──────────────────────────────────────────────────

    @app.exception_handler(LowConfidenceError)
    async def low_confidence_handler(request: Request, exc: LowConfidenceError):
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={"error": "LOW_CONFIDENCE", "message": exc.message, "detail": exc.detail},
        )

    @app.exception_handler(InferenceError)
    async def inference_error_handler(request: Request, exc: InferenceError):
        logger.error("inference_error", path=str(request.url), error=exc.message)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"error": "INFERENCE_ERROR", "message": exc.message, "detail": exc.detail},
        )

    @app.exception_handler(ModelNotLoadedError)
    async def model_not_loaded_handler(request: Request, exc: ModelNotLoadedError):
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={"error": "MODEL_NOT_LOADED", "message": exc.message, "detail": exc.detail},
        )

    @app.exception_handler(StorageError)
    async def storage_error_handler(request: Request, exc: StorageError):
        logger.error("storage_error", error=exc.message)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"error": "STORAGE_ERROR", "message": "Image storage failed.", "detail": {}},
        )

    @app.exception_handler(WeatherAPIError)
    async def weather_api_error_handler(request: Request, exc: WeatherAPIError):
        logger.warning("weather_api_error", error=exc.message)
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={"error": "WEATHER_API_ERROR", "message": "Weather data temporarily unavailable.", "detail": {}},
        )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception):
        logger.error("unhandled_exception", path=str(request.url), error=str(exc), exc_info=True)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error": "INTERNAL_ERROR",
                "message": "An unexpected error occurred. Please try again.",
                "detail": {},
            },
        )

    # ── Health Check ─────────────────────────────────────────────────────────

    @app.get("/health", tags=["system"], summary="Health check: DB, Redis, and ML model")
    async def health_check():
        """
        Verify connectivity to PostgreSQL, Redis, and ML model readiness.
        Returns 200 if all systems are operational, 503 otherwise.
        """
        health = {
            "status": "ok",
            "database": "unknown",
            "redis": "unknown",
            "model": "unknown",
        }

        # Check DB
        try:
            async with AsyncSessionLocal() as db:
                await db.execute(__import__("sqlalchemy").text("SELECT 1"))
            health["database"] = "ok"
        except Exception as exc:
            health["database"] = f"error: {exc}"
            health["status"] = "degraded"

        # Check Redis
        try:
            redis = aioredis.from_url(settings.REDIS_URL)
            await redis.ping()
            await redis.aclose()
            health["redis"] = "ok"
        except Exception as exc:
            health["redis"] = f"error: {exc}"
            health["status"] = "degraded"

        # Check ML model
        if ModelLoader.is_loaded():
            health["model"] = "tflite" if ModelLoader.is_tflite() else "keras"
        else:
            health["model"] = "not_loaded"
            health["status"] = "degraded"

        http_status = status.HTTP_200_OK if health["status"] == "ok" else status.HTTP_503_SERVICE_UNAVAILABLE
        return JSONResponse(content=health, status_code=http_status)

    return app


app = create_app()
