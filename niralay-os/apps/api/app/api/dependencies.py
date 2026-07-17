"""
Shared FastAPI dependencies for NiralayOS.

Sprint 1: get_db, get_settings, get_request_id, get_pagination
Sprint 2: get_current_user, get_current_active_user, require_permission
"""

from __future__ import annotations

from typing import Generator

import jwt
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.security import decode_token
from app.core.settings import Settings, get_settings as _get_settings
from app.database.session import get_db as _get_db
from app.models.user import User

_bearer = HTTPBearer(auto_error=False)


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


# ---------------------------------------------------------------------------
# Authentication — Sprint 2
# ---------------------------------------------------------------------------
def get_current_user(
    request: Request,
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer),
    db: Session = Depends(get_db),
) -> User:
    """
    Decode the bearer JWT and return the authenticated User.

    Raises HTTP 401 if the token is missing, invalid, or expired.
    """
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        payload = decode_token(credentials.credentials)
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Access token has expired.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid access token.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if payload.refresh:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token cannot be used here.",
        )

    from app.repositories.user import UserRepository
    from uuid import UUID

    try:
        user_uuid = UUID(payload.sub)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Malformed token subject.")

    user = UserRepository(db).get_by_uuid(user_uuid)
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or deactivated.",
        )

    # Store JTI on request state for logout / audit use
    request.state.jti = payload.jti
    request.state.current_user = user
    return user


def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """Like get_current_user but also asserts the account is not locked/suspended."""
    if current_user.is_locked:
        raise HTTPException(
            status_code=status.HTTP_423_LOCKED,
            detail="Account is temporarily locked.",
        )
    if current_user.status != "active":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is not active.",
        )
    return current_user


def require_permission(code: str):  # type: ignore[return]
    """
    Dependency factory that checks the current user holds a given permission.

    Usage:
        @router.get("/reservations", dependencies=[Depends(require_permission("reservation:view"))])
        def list_reservations(...): ...
    """
    def _check(current_user: User = Depends(get_current_active_user)) -> User:
        if current_user.is_superuser:
            return current_user  # superusers bypass all checks
        if code not in current_user.permission_codes:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission '{code}' required.",
            )
        return current_user
    return _check
