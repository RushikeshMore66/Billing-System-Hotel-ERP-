"""
Health check endpoints — /api/v1/health

Provides two levels of detail:
  GET /api/v1/health        — basic liveness (always fast)
  GET /api/v1/health/ready  — readiness, includes DB connectivity

Used by:
  - Kubernetes liveness / readiness probes
  - Load-balancer health checks
  - Monitoring dashboards
"""

from __future__ import annotations

import platform
import sys
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse

from app.core.settings import Settings
from app.api.dependencies import get_settings, get_request_id
from app.database.health import check_database_health, get_database_info
from app.schemas.base import SuccessResponse

router = APIRouter(prefix="/health", tags=["Health"])

_START_TIME = datetime.now(timezone.utc)


@router.get(
    "",
    summary="Liveness probe",
    description="Returns 200 as long as the API process is running. Does not check dependencies.",
    response_model=SuccessResponse[dict],
)
async def liveness(
    request: Request,
    settings: Settings = Depends(get_settings),
    request_id: str = Depends(get_request_id),
):
    """Fast liveness check — does NOT touch the database."""
    uptime_seconds = (datetime.now(timezone.utc) - _START_TIME).total_seconds()
    data = {
        "status": "ok",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT.value,
        "uptime_seconds": round(uptime_seconds, 2),
    }
    return SuccessResponse.of(data=data, message="Alive", request_id=request_id)


@router.get(
    "/ready",
    summary="Readiness probe",
    description="Returns 200 only if all critical dependencies (database) are reachable.",
    response_model=SuccessResponse[dict],
)
async def readiness(
    request: Request,
    settings: Settings = Depends(get_settings),
    request_id: str = Depends(get_request_id),
):
    """Full readiness check — verifies database connectivity."""
    db_healthy, db_message = await check_database_health()
    db_info = await get_database_info()

    uptime_seconds = (datetime.now(timezone.utc) - _START_TIME).total_seconds()

    data = {
        "status": "ok" if db_healthy else "degraded",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT.value,
        "uptime_seconds": round(uptime_seconds, 2),
        "python_version": sys.version.split()[0],
        "platform": platform.system(),
        "dependencies": {
            "database": {
                "status": "ok" if db_healthy else "error",
                "message": db_message,
                **db_info,
            },
        },
    }

    http_status = 200 if db_healthy else 503
    return JSONResponse(
        status_code=http_status,
        content=SuccessResponse.of(
            data=data,
            message="Ready" if db_healthy else "Degraded — database unreachable",
            request_id=request_id,
        ).model_dump(mode="json"),
    )
