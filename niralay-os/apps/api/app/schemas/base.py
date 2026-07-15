"""
Base response schemas for NiralayOS.

Every API endpoint returns one of these shapes:
  - SuccessResponse[T]  — data payload with metadata
  - ErrorResponse       — structured error with code and details
  - PaginatedResponse[T]— paginated list with navigation metadata

Usage:
    from app.schemas.base import SuccessResponse, ErrorResponse, PaginatedResponse

    @router.get("/rooms", response_model=PaginatedResponse[RoomOut])
    def list_rooms(...):
        ...
        return PaginatedResponse.build(items=rooms, total=total, page=page, size=size)
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Generic, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")

_APP_VERSION = None


def _get_version() -> str:
    global _APP_VERSION
    if _APP_VERSION is None:
        try:
            from app.core.settings import get_settings
            _APP_VERSION = get_settings().APP_VERSION
        except Exception:
            _APP_VERSION = "1.0.0"
    return _APP_VERSION


# ---------------------------------------------------------------------------
# Response envelope
# ---------------------------------------------------------------------------
class ResponseMeta(BaseModel):
    """Metadata attached to every API response."""

    request_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    version: str = Field(default_factory=_get_version)


class SuccessResponse(BaseModel, Generic[T]):
    """
    Standard success envelope.

    Example:
        {
            "success": true,
            "data": { ... },
            "message": "Room created",
            "meta": { "request_id": "...", "timestamp": "..." }
        }
    """

    success: bool = True
    data: T
    message: str = "ok"
    meta: ResponseMeta = Field(default_factory=ResponseMeta)

    @classmethod
    def of(
        cls,
        data: T,
        message: str = "ok",
        request_id: str | None = None,
    ) -> "SuccessResponse[T]":
        meta = ResponseMeta()
        if request_id:
            meta.request_id = request_id
        return cls(data=data, message=message, meta=meta)


class ErrorDetail(BaseModel):
    """A single validation or business-rule error."""

    field: str | None = None
    message: str
    code: str | None = None


class ErrorResponse(BaseModel):
    """
    Standard error envelope.

    Example:
        {
            "success": false,
            "error_code": "ROOM_NOT_FOUND",
            "message": "Room 42 does not exist",
            "details": [],
            "meta": { ... }
        }
    """

    success: bool = False
    error_code: str
    message: str
    details: list[ErrorDetail] = []
    meta: ResponseMeta = Field(default_factory=ResponseMeta)

    @classmethod
    def of(
        cls,
        error_code: str,
        message: str,
        details: list[ErrorDetail] | None = None,
        request_id: str | None = None,
    ) -> "ErrorResponse":
        meta = ResponseMeta()
        if request_id:
            meta.request_id = request_id
        return cls(
            error_code=error_code,
            message=message,
            details=details or [],
            meta=meta,
        )


class PaginationMeta(BaseModel):
    """Pagination navigation metadata."""

    page: int
    page_size: int
    total: int
    total_pages: int
    has_next: bool
    has_prev: bool


class PaginatedResponse(BaseModel, Generic[T]):
    """
    Standard paginated list envelope.

    Example:
        {
            "success": true,
            "data": [...],
            "pagination": { "page": 1, "page_size": 20, "total": 150, ... },
            "meta": { ... }
        }
    """

    success: bool = True
    data: list[T]
    pagination: PaginationMeta
    meta: ResponseMeta = Field(default_factory=ResponseMeta)

    @classmethod
    def build(
        cls,
        items: list[T],
        total: int,
        page: int,
        size: int,
        request_id: str | None = None,
    ) -> "PaginatedResponse[T]":
        total_pages = max(1, -(-total // size))  # ceiling division
        meta = ResponseMeta()
        if request_id:
            meta.request_id = request_id
        pagination = PaginationMeta(
            page=page,
            page_size=size,
            total=total,
            total_pages=total_pages,
            has_next=page < total_pages,
            has_prev=page > 1,
        )
        return cls(data=items, pagination=pagination, meta=meta)


# ---------------------------------------------------------------------------
# Common field schemas
# ---------------------------------------------------------------------------
class IDSchema(BaseModel):
    id: int
    uuid: uuid.UUID


class TimestampSchema(BaseModel):
    created_at: datetime
    updated_at: datetime


class AuditSchema(IDSchema, TimestampSchema):
    """Full audit field set — used as mixin for output schemas."""

    created_by: str | None = None
    updated_by: str | None = None
    is_active: bool = True
