"""
Activity widget service for NiralayOS Dashboard.

Maps audit log events to human-readable dashboard activity items.
Uses the immutable AuditLog table as the single source of truth.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.repositories.dashboard import DashboardRepository
from app.schemas.dashboard import ActivityItem, ActivityWidget

# Mapping from audit event code → dashboard event_type + description template
_EVENT_MAP: dict[str, tuple[str, str]] = {
    "LOGIN": ("guest_checked_in", "User logged in"),
    "LOGOUT": ("guest_checked_out", "User logged out"),
    "LOGIN_FAILED": ("guest_checked_in", "Failed login attempt"),
    "ACCOUNT_LOCKED": ("guest_checked_in", "Account locked after failed attempts"),
    "USER_CREATED": ("reservation_created", "New user account created"),
    "USER_UPDATED": ("reservation_created", "User account updated"),
    "USER_DEACTIVATED": ("guest_checked_out", "User account deactivated"),
    "PASSWORD_CHANGED": ("invoice_paid", "Password changed"),
    "PASSWORD_RESET_REQUESTED": ("invoice_paid", "Password reset requested"),
    "PASSWORD_RESET": ("invoice_paid", "Password reset completed"),
    "ROLE_ASSIGNED": ("employee_clock_in", "Role assigned to user"),
    "ROLE_REVOKED": ("employee_clock_in", "Role revoked from user"),
    "TOKEN_REFRESHED": ("employee_clock_in", "Authentication token refreshed"),
}


class ActivityService:
    """Business logic for the Activity Feed widget."""

    def __init__(self, db: Session) -> None:
        self._repo = DashboardRepository(db)

    def get_widget(self, limit: int = 20, skip: int = 0) -> ActivityWidget:
        total = self._repo.count_activities()
        raw = self._repo.get_recent_activities(limit=limit, skip=skip)
        activities = [self._map_activity(row) for row in raw]
        return ActivityWidget(activities=activities, total=total)

    def get_activities(self, limit: int = 20, skip: int = 0) -> list[ActivityItem]:
        raw = self._repo.get_recent_activities(limit=limit, skip=skip)
        return [self._map_activity(row) for row in raw]

    # ----------------------------------------------------------------
    # Helpers
    # ----------------------------------------------------------------
    def _map_activity(self, row: dict) -> ActivityItem:
        event_code: str = row.get("event", "UNKNOWN")
        event_type, default_description = _EVENT_MAP.get(
            event_code, ("employee_clock_in", event_code.replace("_", " ").title())
        )

        detail: str = row.get("detail") or default_description

        # Parse metadata JSON if present
        metadata: dict = {}
        raw_meta = row.get("metadata_json")
        if raw_meta:
            try:
                metadata = json.loads(raw_meta)
            except (json.JSONDecodeError, TypeError):
                pass

        occurred: datetime = row.get("created_at", datetime.now(timezone.utc))
        if isinstance(occurred, datetime) and occurred.tzinfo is None:
            occurred = occurred.replace(tzinfo=timezone.utc)

        return ActivityItem(
            id=row["id"],
            event_type=event_type,
            description=detail,
            actor=row.get("actor_name") or row.get("actor_uuid"),
            resource_id=row.get("resource_id"),
            metadata=metadata,
            occurred_at=occurred,
        )
