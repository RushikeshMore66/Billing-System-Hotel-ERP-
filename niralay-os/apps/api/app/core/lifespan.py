"""
FastAPI application lifespan context manager.

Manages startup and shutdown events:
  - Configure logging
  - Verify database connectivity
  - (Future) Start background workers, connect Redis, etc.

Usage in main.py:
    app = FastAPI(lifespan=lifespan)
"""

from __future__ import annotations

from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI

from app.core.logging import configure_logging, get_logger
from app.core.settings import get_settings
from app.database.health import check_database_health

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """
    Application lifespan handler.

    Runs startup logic before yielding, then shutdown logic after.
    """
    # ---- Startup --------------------------------------------------------
    configure_logging()
    cfg = get_settings()

    logger.info(
        "Starting %s v%s",
        cfg.APP_NAME,
        cfg.APP_VERSION,
        extra={
            "environment": cfg.ENVIRONMENT.value,
            "debug": cfg.DEBUG,
            "api_prefix": cfg.API_PREFIX,
        },
    )

    # Verify database is reachable at startup
    db_ok, db_msg = await check_database_health()
    if db_ok:
        logger.info("Database connection verified", extra={"detail": db_msg})
    else:
        logger.warning(
            "Database not reachable at startup — some endpoints will fail",
            extra={"detail": db_msg},
        )

    logger.info(
        "%s is ready to serve requests on %s:%s",
        cfg.APP_NAME,
        cfg.SERVER_HOST,
        cfg.SERVER_PORT,
    )

    if db_ok:
        try:
            from app.database.session import get_session_factory
            from app.core.seeder import seed_database
            SessionFactory = get_session_factory()
            with SessionFactory() as db:
                seed_database(db)
                db.commit()
        except Exception as e:
            logger.error("Database seeding failed: %s", e)

    yield  # Application runs here

    # ---- Shutdown -------------------------------------------------------
    logger.info("Shutting down %s", cfg.APP_NAME)
    # Future: close Redis connections, stop background tasks, etc.
