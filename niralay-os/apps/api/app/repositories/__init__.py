"""
Repositories package for NiralayOS.
"""

from app.repositories.base import BaseRepository
from app.repositories.user import (
    UserRepository,
    PasswordHistoryRepository,
    UserPreferenceRepository,
)
from app.repositories.role import RoleRepository, PermissionRepository
from app.repositories.session import (
    SessionRepository,
    RefreshTokenRepository,
    AuditLogRepository,
)
from app.repositories.dashboard import DashboardRepository

__all__ = [
    "BaseRepository",
    "UserRepository",
    "PasswordHistoryRepository",
    "UserPreferenceRepository",
    "RoleRepository",
    "PermissionRepository",
    "SessionRepository",
    "RefreshTokenRepository",
    "AuditLogRepository",
    "DashboardRepository",
]

