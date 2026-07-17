"""
Audit service for NiralayOS.

Thin wrapper around AuditLogRepository.
Must be called from other services for every security event.
"""

from __future__ import annotations

import json
from typing import Any, Optional

from sqlalchemy.orm import Session

from app.models.audit_log import AuditLog
from app.repositories.session import AuditLogRepository


class AuditService:
    """Append-only security event logger."""

    def __init__(self, db: Session) -> None:
        self._repo = AuditLogRepository(db)

    def log(
        self,
        event: str,
        *,
        actor_id: Optional[int] = None,
        actor_uuid: Optional[str] = None,
        resource_type: Optional[str] = None,
        resource_id: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        outcome: str = "success",
        detail: Optional[str] = None,
        metadata: Optional[dict[str, Any]] = None,
    ) -> None:
        entry = AuditLog(
            actor_id=actor_id,
            actor_uuid=actor_uuid,
            event=event,
            resource_type=resource_type,
            resource_id=resource_id,
            ip_address=ip_address,
            user_agent=user_agent,
            outcome=outcome,
            detail=detail,
            metadata_json=json.dumps(metadata) if metadata else None,
        )
        self._repo.append(entry)
