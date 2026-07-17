"""
Models package for NiralayOS.

Import all models here so that:
  1. SQLAlchemy's mapper registry is populated before Alembic runs autogenerate.
  2. Relationship back-refs resolve correctly at runtime.

Usage:
    from app.models import User, Role, Permission, Session, RefreshToken, AuditLog
"""

from app.models.user import User, PasswordHistory, UserPreference, user_roles
from app.models.role import Role, Permission, role_permissions
from app.models.session import Session, RefreshToken
from app.models.audit_log import AuditLog

__all__ = [
    "User",
    "PasswordHistory",
    "UserPreference",
    "user_roles",
    "Role",
    "Permission",
    "role_permissions",
    "Session",
    "RefreshToken",
    "AuditLog",
]
