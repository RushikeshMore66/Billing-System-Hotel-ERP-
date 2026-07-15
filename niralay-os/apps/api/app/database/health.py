"""
Database health check for NiralayOS.

Provides a lightweight connectivity probe used by:
  - Application lifespan (startup verification)
  - /health and /api/v1/health endpoints
  - Kubernetes / load-balancer readiness probes

Returns a tuple[bool, str] — (is_healthy, detail_message)
so callers can decide how to surface the result.
"""

from __future__ import annotations

import time
from typing import NamedTuple

from sqlalchemy import text
from sqlalchemy.exc import OperationalError, SQLAlchemyError

from app.core.logging import get_logger

logger = get_logger(__name__)


class DatabaseHealthResult(NamedTuple):
    healthy: bool
    message: str
    latency_ms: float


async def check_database_health() -> tuple[bool, str]:
    """
    Probe the database with a lightweight SELECT 1.

    Returns:
        (True, "ok") if reachable.
        (False, <error detail>) if not reachable.

    This function is safe to call from both async and sync contexts.
    It does *not* hold a session open longer than necessary.
    """
    from app.database.session import get_session_factory

    start = time.perf_counter()
    try:
        SessionFactory = get_session_factory()
        with SessionFactory() as session:
            session.execute(text("SELECT 1"))
        latency_ms = (time.perf_counter() - start) * 1000
        logger.debug("DB health check passed", extra={"latency_ms": round(latency_ms, 2)})
        return True, f"ok ({latency_ms:.1f} ms)"
    except OperationalError as exc:
        latency_ms = (time.perf_counter() - start) * 1000
        detail = f"OperationalError: {exc.orig}"
        logger.warning("DB health check failed", extra={"error": detail})
        return False, detail
    except SQLAlchemyError as exc:
        latency_ms = (time.perf_counter() - start) * 1000
        detail = f"SQLAlchemyError: {exc}"
        logger.warning("DB health check failed", extra={"error": detail})
        return False, detail
    except Exception as exc:
        latency_ms = (time.perf_counter() - start) * 1000
        detail = f"Unexpected error: {exc}"
        logger.error("DB health check unexpected error", extra={"error": detail})
        return False, detail


async def get_database_info() -> dict:
    """
    Return database server version and connection pool stats.

    Used by the detailed health endpoint.
    """
    from app.database.session import get_engine

    try:
        eng = get_engine()
        with eng.connect() as conn:
            row = conn.execute(text("SELECT version()")).scalar()
        pool = eng.pool
        return {
            "server_version": row,
            "pool_size": pool.size(),
            "checked_in": pool.checkedin(),
            "checked_out": pool.checkedout(),
            "overflow": pool.overflow(),
        }
    except Exception as exc:
        return {"error": str(exc)}
