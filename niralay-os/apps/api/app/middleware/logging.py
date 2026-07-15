"""
Request / response access logging middleware.

Logs every HTTP request with:
  - method, path, status code
  - request duration (ms)
  - client IP
  - request ID

Skips logging for health-check endpoints to reduce noise.
"""

from __future__ import annotations

import time
import logging

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response
from starlette.types import ASGIApp

logger = logging.getLogger("niralayos.access")

# Paths that should NOT be logged (noisy health probes)
_SKIP_PATHS: frozenset[str] = frozenset({"/health", "/ping", "/favicon.ico"})


class LoggingMiddleware(BaseHTTPMiddleware):
    """Log every HTTP request with timing and metadata."""

    def __init__(self, app: ASGIApp) -> None:
        super().__init__(app)

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        if request.url.path in _SKIP_PATHS:
            return await call_next(request)

        start = time.perf_counter()
        request_id = getattr(request.state, "request_id", "-")

        try:
            response: Response = await call_next(request)
        except Exception as exc:
            duration_ms = (time.perf_counter() - start) * 1000
            logger.error(
                "Request failed",
                extra={
                    "method": request.method,
                    "path": request.url.path,
                    "client": _get_client_ip(request),
                    "request_id": request_id,
                    "duration_ms": round(duration_ms, 2),
                    "error": str(exc),
                },
            )
            raise

        duration_ms = (time.perf_counter() - start) * 1000
        level = logging.WARNING if response.status_code >= 400 else logging.INFO

        logger.log(
            level,
            "%s %s %s",
            request.method,
            request.url.path,
            response.status_code,
            extra={
                "method": request.method,
                "path": request.url.path,
                "query": str(request.url.query) or None,
                "status_code": response.status_code,
                "client": _get_client_ip(request),
                "request_id": request_id,
                "duration_ms": round(duration_ms, 2),
            },
        )

        return response


def _get_client_ip(request: Request) -> str:
    """Extract the real client IP, respecting reverse-proxy headers."""
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()
    if request.client:
        return request.client.host
    return "unknown"
