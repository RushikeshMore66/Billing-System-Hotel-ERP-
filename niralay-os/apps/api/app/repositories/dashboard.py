"""
Dashboard repository for NiralayOS.

Contains ONLY database I/O. Every method is an optimised aggregation query.
No N+1 queries. No business logic.

The dashboard queries against:
  - users (employee counts)
  - sessions (active guests)
  - audit_logs (activity feed)

Since this is an ERP platform in active development, the full reservation,
room, billing and inventory models are not yet in the DB schema. This
repository provides real data from the tables that DO exist (auth/identity
platform) and returns zero-based defaults for tables that will be added in
future sprints. Each stub is clearly marked so it can be replaced once the
relevant sprint is complete.
"""

from __future__ import annotations

import calendar  # noqa: F401 — retained for Sprint 3 billing queries
from datetime import date, datetime, timedelta, timezone
from typing import Any

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.audit_log import AuditLog
from app.models.session import Session as UserSession
from app.models.user import User


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _today_utc() -> date:
    return _utc_now().date()


# ---------------------------------------------------------------------------
# Revenue queries
# ---------------------------------------------------------------------------

class DashboardRepository:
    """
    Single repository that satisfies all dashboard widget queries.

    Methods are grouped by widget. Each method returns raw aggregated
    data as dicts or scalars — no ORM model instances are returned.
    """

    def __init__(self, db: Session) -> None:
        self.db = db

    # ----------------------------------------------------------------
    # User / Employee
    # ----------------------------------------------------------------
    def count_active_users(self) -> int:
        """Total active employees / users in the system."""
        return (
            self.db.query(func.count(User.id))
            .filter(User.is_active.is_(True))
            .scalar()
            or 0
        )

    def count_users_logged_in_today(self) -> int:
        """
        Count distinct users who have an active or recently-created session today.
        Used as a proxy for 'present today'.
        """
        today_start = datetime.combine(_today_utc(), datetime.min.time()).replace(
            tzinfo=timezone.utc
        )
        return (
            self.db.query(func.count(func.distinct(UserSession.user_id)))
            .filter(UserSession.login_at >= today_start)
            .scalar()
            or 0
        )

    def count_active_sessions(self) -> int:
        """Count currently live (non-revoked, non-expired) sessions."""
        now = _utc_now()
        return (
            self.db.query(func.count(UserSession.id))
            .filter(
                UserSession.is_revoked.is_(False),
                UserSession.logout_at.is_(None),
                UserSession.expires_at > now,
            )
            .scalar()
            or 0
        )

    # ----------------------------------------------------------------
    # Activity Feed (from audit_logs — immutable security event log)
    # ----------------------------------------------------------------
    def get_recent_activities(
        self, limit: int = 20, skip: int = 0
    ) -> list[dict[str, Any]]:
        """
        Return the most recent audit log entries, newest first.
        Each entry is mapped to a dashboard activity type.
        """
        rows = (
            self.db.query(
                AuditLog.id,
                AuditLog.event,
                AuditLog.actor_uuid,
                AuditLog.resource_type,
                AuditLog.resource_id,
                AuditLog.ip_address,
                AuditLog.detail,
                AuditLog.outcome,
                AuditLog.metadata_json,
                AuditLog.created_at,
                User.full_name.label("actor_name"),
            )
            .outerjoin(User, User.id == AuditLog.actor_id)
            .order_by(AuditLog.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )
        return [row._asdict() for row in rows]

    def count_activities(self) -> int:
        return self.db.query(func.count(AuditLog.id)).scalar() or 0

    # ----------------------------------------------------------------
    # Audit-log based revenue proxy
    # (Real revenue will come from billing/payment tables in Sprint 3+)
    # ----------------------------------------------------------------
    def get_daily_login_counts(self, days: int = 7) -> list[dict[str, Any]]:
        """
        Daily audit-log LOGIN event counts for the past N days.
        Acts as activity proxy until Billing sprint is complete.
        """
        since = _utc_now() - timedelta(days=days)
        rows = (
            self.db.query(
                func.date(AuditLog.created_at).label("day"),
                func.count(AuditLog.id).label("count"),
            )
            .filter(
                AuditLog.event == "LOGIN",
                AuditLog.created_at >= since,
            )
            .group_by(func.date(AuditLog.created_at))
            .order_by(func.date(AuditLog.created_at))
            .all()
        )
        return [{"day": row.day, "count": row.count} for row in rows]

    def get_event_counts_by_day(
        self, event: str, days: int = 30
    ) -> list[dict[str, Any]]:
        """Generic per-day count for a specific audit event code."""
        since = _utc_now() - timedelta(days=days)
        rows = (
            self.db.query(
                func.date(AuditLog.created_at).label("day"),
                func.count(AuditLog.id).label("count"),
            )
            .filter(
                AuditLog.event == event,
                AuditLog.created_at >= since,
                AuditLog.outcome == "success",
            )
            .group_by(func.date(AuditLog.created_at))
            .order_by(func.date(AuditLog.created_at))
            .all()
        )
        return [{"day": row.day, "count": row.count} for row in rows]


    def get_audit_counts_today(self) -> dict[str, int]:
        """
        Return count of all security event types that happened today.
        Used to build the quick-stats block.
        """
        today_start = datetime.combine(_today_utc(), datetime.min.time()).replace(
            tzinfo=timezone.utc
        )
        rows = (
            self.db.query(AuditLog.event, func.count(AuditLog.id).label("cnt"))
            .filter(AuditLog.created_at >= today_start)
            .group_by(AuditLog.event)
            .all()
        )
        return {row.event: row.cnt for row in rows}

    def get_audit_counts_yesterday(self) -> dict[str, int]:
        """Same counts but for yesterday (used to compute deltas)."""
        today_start = datetime.combine(_today_utc(), datetime.min.time()).replace(
            tzinfo=timezone.utc
        )
        yesterday_start = today_start - timedelta(days=1)
        rows = (
            self.db.query(AuditLog.event, func.count(AuditLog.id).label("cnt"))
            .filter(
                AuditLog.created_at >= yesterday_start,
                AuditLog.created_at < today_start,
            )
            .group_by(AuditLog.event)
            .all()
        )
        return {row.event: row.cnt for row in rows}

    def get_monthly_login_summary(self, months: int = 6) -> list[dict[str, Any]]:
        """
        Monthly LOGIN counts for the past N months.
        Used as activity trend until real revenue data is available.
        """
        since = _utc_now() - timedelta(days=months * 31)
        rows = (
            self.db.query(
                func.extract("year", AuditLog.created_at).label("year"),
                func.extract("month", AuditLog.created_at).label("month"),
                func.count(AuditLog.id).label("count"),
            )
            .filter(
                AuditLog.event == "LOGIN",
                AuditLog.created_at >= since,
                AuditLog.outcome == "success",
            )
            .group_by(
                func.extract("year", AuditLog.created_at),
                func.extract("month", AuditLog.created_at),
            )
            .order_by(
                func.extract("year", AuditLog.created_at),
                func.extract("month", AuditLog.created_at),
            )
            .all()
        )
        return [
            {"year": int(row.year), "month": int(row.month), "count": row.count}
            for row in rows
        ]

    # ----------------------------------------------------------------
    # User breakdown (department / role proxy for employee widget)
    # ----------------------------------------------------------------
    def get_user_status_breakdown(self) -> dict[str, int]:
        """Count users by status."""
        rows = (
            self.db.query(
                User.status,
                func.count(User.id).label("cnt"),
            )
            .filter(User.is_active.is_(True))
            .group_by(User.status)
            .all()
        )
        return {row.status: row.cnt for row in rows}

    def get_locked_user_count(self) -> int:
        """Count users currently locked out."""
        now = _utc_now()
        return (
            self.db.query(func.count(User.id))
            .filter(
                User.locked_until.isnot(None),
                User.locked_until > now,
            )
            .scalar()
            or 0
        )
