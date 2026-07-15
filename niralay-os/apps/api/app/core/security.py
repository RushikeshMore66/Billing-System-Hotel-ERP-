"""
Security utilities for NiralayOS.

Covers:
  - Password hashing / verification  (bcrypt)
  - JWT access token creation / decoding
  - Refresh token creation / decoding
  - Token payload model
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any, Optional
from uuid import uuid4

import bcrypt
import jwt
from pydantic import BaseModel, Field

from app.core.settings import get_settings
from app.core.constants import TOKEN_TYPE_BEARER

# ---------------------------------------------------------------------------
# Password hashing  (using bcrypt directly — passlib has bcrypt>=4 compat issues)
# ---------------------------------------------------------------------------
_BCRYPT_ROUNDS: int = 12


def hash_password(plain: str) -> str:
    """Return a bcrypt hash of *plain*."""
    return bcrypt.hashpw(
        plain.encode("utf-8"),
        bcrypt.gensalt(rounds=_BCRYPT_ROUNDS),
    ).decode("utf-8")


def verify_password(plain: str, hashed: str) -> bool:
    """Return True if *plain* matches *hashed*."""
    return bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8"))


# ---------------------------------------------------------------------------
# Token payload
# ---------------------------------------------------------------------------
class TokenPayload(BaseModel):
    """
    Data stored inside a JWT.

    All fields match registered / public claim names where applicable.
    role and permissions are optional because refresh tokens omit them.
    """

    sub: str                              # user UUID string
    role: Optional[str] = None            # None for refresh tokens
    permissions: list[str] = []           # empty for refresh tokens
    jti: str = Field(default_factory=lambda: str(uuid4()))  # unique token ID
    iat: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    exp: Optional[datetime] = None
    refresh: bool = False                 # True only for refresh tokens


class TokenPair(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = TOKEN_TYPE_BEARER
    expires_in: int  # seconds until access token expiry


# ---------------------------------------------------------------------------
# JWT helpers
# ---------------------------------------------------------------------------
def _now_utc() -> datetime:
    return datetime.now(timezone.utc)


def create_access_token(
    subject: str,
    role: str,
    permissions: list[str],
    extra_claims: dict[str, Any] | None = None,
) -> str:
    """
    Issue a signed JWT access token.

    Args:
        subject:     User UUID (as string).
        role:        User's primary role.
        permissions: List of granted permission codes.
        extra_claims: Additional custom claims to embed.

    Returns:
        Signed JWT string.
    """
    cfg = get_settings()
    now = _now_utc()
    expire = now + timedelta(minutes=cfg.ACCESS_TOKEN_EXPIRE_MINUTES)

    payload: dict[str, Any] = {
        "sub": subject,
        "role": role,
        "permissions": permissions,
        "jti": str(uuid4()),
        "iat": int(now.timestamp()),
        "exp": int(expire.timestamp()),
        "refresh": False,
    }
    if extra_claims:
        payload.update(extra_claims)

    return jwt.encode(payload, cfg.SECRET_KEY, algorithm=cfg.ALGORITHM)


def create_refresh_token(subject: str) -> str:
    """
    Issue a signed JWT refresh token.

    The refresh token carries *only* the subject — no role or permissions —
    to minimise the blast radius if intercepted.
    """
    cfg = get_settings()
    now = _now_utc()
    expire = now + timedelta(days=cfg.REFRESH_TOKEN_EXPIRE_DAYS)

    payload: dict[str, Any] = {
        "sub": subject,
        "jti": str(uuid4()),
        "iat": int(now.timestamp()),
        "exp": int(expire.timestamp()),
        "refresh": True,
    }
    return jwt.encode(payload, cfg.SECRET_KEY, algorithm=cfg.ALGORITHM)


def decode_token(token: str) -> TokenPayload:
    """
    Decode and validate a JWT.

    Raises:
        jwt.ExpiredSignatureError: Token has expired.
        jwt.InvalidTokenError:     Token is otherwise invalid.
    """
    cfg = get_settings()
    raw: dict[str, Any] = jwt.decode(
        token,
        cfg.SECRET_KEY,
        algorithms=[cfg.ALGORITHM],
    )
    # Convert integer timestamps back to datetime objects
    if isinstance(raw.get("iat"), (int, float)):
        raw["iat"] = datetime.fromtimestamp(raw["iat"], tz=timezone.utc)
    if isinstance(raw.get("exp"), (int, float)):
        raw["exp"] = datetime.fromtimestamp(raw["exp"], tz=timezone.utc)

    return TokenPayload(**raw)


def create_token_pair(
    subject: str,
    role: str,
    permissions: list[str],
) -> TokenPair:
    """Convenience function: create both access and refresh tokens."""
    cfg = get_settings()
    access = create_access_token(subject, role, permissions)
    refresh = create_refresh_token(subject)
    return TokenPair(
        access_token=access,
        refresh_token=refresh,
        token_type=TOKEN_TYPE_BEARER,
        expires_in=cfg.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )
