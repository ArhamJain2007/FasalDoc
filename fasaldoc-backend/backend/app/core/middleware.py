"""
Custom middleware: structured request logging.
Rate limiting is configured per-endpoint using slowapi decorators.
"""
import time
import structlog
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

logger = structlog.get_logger()


class LoggingMiddleware(BaseHTTPMiddleware):
    """
    Log every HTTP request with method, path, status, and duration.
    Uses structlog for JSON-formatted output in production.
    """

    async def dispatch(self, request: Request, call_next) -> Response:
        """
        Process request through the middleware chain, recording timing info.

        Args:
            request: Incoming HTTP request.
            call_next: Next middleware or route handler.
        Returns:
            HTTP response with all headers intact.
        """
        start = time.perf_counter()

        try:
            response = await call_next(request)
        except Exception as exc:
            duration = round((time.perf_counter() - start) * 1000, 1)
            logger.error(
                "request_error",
                method=request.method,
                path=request.url.path,
                duration_ms=duration,
                error=str(exc),
                user_agent=request.headers.get("user-agent", ""),
            )
            raise

        duration = round((time.perf_counter() - start) * 1000, 1)
        logger.info(
            "request",
            method=request.method,
            path=request.url.path,
            status=response.status_code,
            duration_ms=duration,
            user_agent=request.headers.get("user-agent", ""),
            content_length=response.headers.get("content-length"),
        )
        return response
