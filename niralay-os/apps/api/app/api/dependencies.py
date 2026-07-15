"""
Shared FastAPI dependencies for NiralayOS.

Each function in this module is a FastAPI dependency — injected via
``Depends(...)`` in route handlers.

Sprint 1 provides:
  - get_db       — database session (re-exported from database.session)
  - get_settings — settings singleton

Sprint 2 will add:
  - get_current_user
  - require_permission(...)
  - get_current_active_user
"""

from __future__ import annotations

from typing import Generator

from fastapi import HTTPException, Request, status
from sqlalchemy.orm import Session

from app.core.settings import Settings, get_settings as _get_settings
from app.database.session import get_db as _get_db


# ---------------------------------------------------------------------------
# Database
# ---------------------------------------------------------------------------
def get_db() -> Generator[Session, None, None]:
    """Yield a scoped database session for the current request."""
    yield from _get_db()


# ---------------------------------------------------------------------------
# Settings
# ---------------------------------------------------------------------------
def get_settings() -> Settings:
    """Return the application settings singleton."""
    return _get_settings()


# ---------------------------------------------------------------------------
# Request ID
# ---------------------------------------------------------------------------
def get_request_id(request: Request) -> str:
    """Extract the request ID set by RequestIDMiddleware."""
    return getattr(request.state, "request_id", "unknown")


# ---------------------------------------------------------------------------
# Pagination helpers
# ---------------------------------------------------------------------------
def get_pagination(
    page: int = 1,
    size: int = 20,
) -> dict[str, int]:
    """
    Extract and validate pagination parameters.

    Usage:
        @router.get("/items")
        def list_items(pagination: dict = Depends(get_pagination)):
            page = pagination["page"]
            size = pagination["size"]
            offset = pagination["offset"]
    """
    from app.core.constants import MAX_PAGE_SIZE

    if page < 1:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="page must be >= 1",
        )
    size = min(size, MAX_PAGE_SIZE)
    size = max(size, 1)
    return {
        "page": page,
        "size": size,
        "offset": (page - 1) * size,
    }
