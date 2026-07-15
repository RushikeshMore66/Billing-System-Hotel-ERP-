"""
Database session factory for NiralayOS.

Provides:
  - ``engine``            — The SQLAlchemy Engine (synchronous, for Alembic)
  - ``SessionLocal``      — Session factory bound to the engine
  - ``get_db``            — FastAPI dependency that yields a scoped session
  - ``get_db_session``    — Async context manager for use outside of FastAPI

Uses synchronous SQLAlchemy (psycopg2) to keep the stack simple and
compatible with Alembic migrations. Async support (asyncpg) can be
layered on later without changing this interface.
"""

from __future__ import annotations

from contextlib import contextmanager
from typing import Generator

from sqlalchemy import create_engine, event
from sqlalchemy.orm import Session, sessionmaker

from app.core.settings import get_settings
from app.core.logging import get_logger

logger = get_logger(__name__)


def _build_engine():  # type: ignore[return]
    cfg = get_settings()

    connect_args: dict[str, object] = {}
    # psycopg2 requires application_name for connection tracking in pg_stat_activity
    connect_args["application_name"] = cfg.APP_NAME

    engine = create_engine(
        cfg.DATABASE_URL,
        pool_size=cfg.DATABASE_POOL_SIZE,
        max_overflow=cfg.DATABASE_MAX_OVERFLOW,
        pool_timeout=cfg.DATABASE_POOL_TIMEOUT,
        pool_recycle=cfg.DATABASE_POOL_RECYCLE,
        pool_pre_ping=True,          # Detect stale connections automatically
        echo=cfg.DATABASE_ECHO,
        connect_args=connect_args,
    )

    # Log first connection success
    @event.listens_for(engine, "connect")
    def _on_connect(dbapi_conn, connection_record):
        logger.debug("New database connection established")

    return engine


# Lazily built so tests can override settings before first use
_engine = None
_SessionLocal = None


def get_engine():
    global _engine
    if _engine is None:
        _engine = _build_engine()
    return _engine


def get_session_factory() -> sessionmaker[Session]:
    global _SessionLocal
    if _SessionLocal is None:
        _SessionLocal = sessionmaker(
            bind=get_engine(),
            autocommit=False,
            autoflush=False,
            expire_on_commit=False,  # Prevent lazy-load issues after commit
        )
    return _SessionLocal


# Convenience aliases
def engine():
    return get_engine()


def SessionLocal():
    return get_session_factory()


# ---------------------------------------------------------------------------
# FastAPI dependency
# ---------------------------------------------------------------------------
def get_db() -> Generator[Session, None, None]:
    """
    FastAPI dependency — yields a database session per request.

    Usage in a route:
        @router.get("/rooms")
        def list_rooms(db: Session = Depends(get_db)):
            ...
    """
    SessionFactory = get_session_factory()
    db = SessionFactory()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


# ---------------------------------------------------------------------------
# Context manager for use outside FastAPI (scripts, tests, background jobs)
# ---------------------------------------------------------------------------
@contextmanager
def get_db_session() -> Generator[Session, None, None]:
    """
    Context manager that provides a database session.

    Usage:
        with get_db_session() as db:
            db.query(Room).all()
    """
    SessionFactory = get_session_factory()
    db = SessionFactory()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()
