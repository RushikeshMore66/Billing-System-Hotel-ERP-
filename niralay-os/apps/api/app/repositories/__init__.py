"""
Repositories package for NiralayOS.
"""

# ── Sprint 2: Identity & Access ──────────────────────────────────────────────
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

# ── Sprint 3: Property Configuration ────────────────────────────────────────
from app.repositories.property import (
    PropertyProfileRepository,
    FloorRepository,
    AmenityRepository,
    BedTypeRepository,
    RoomTypeRepository,
    RoomRepository,
    TaxRepository,
    PaymentMethodRepository,
    CurrencyRepository,
    SeasonRepository,
    RatePlanRepository,
)
from app.repositories.restaurant import (
    RestaurantCategoryRepository,
    MenuCategoryRepository,
    KitchenStationRepository,
    MenuItemRepository,
    MenuModifierRepository,
    RestaurantTableRepository,
)
from app.repositories.organization import (
    DepartmentRepository,
    DesignationRepository,
    GuestIDTypeRepository,
)
from app.repositories.business_settings import BusinessSettingsRepository

__all__ = [
    # base
    "BaseRepository",
    # identity
    "UserRepository",
    "PasswordHistoryRepository",
    "UserPreferenceRepository",
    "RoleRepository",
    "PermissionRepository",
    "SessionRepository",
    "RefreshTokenRepository",
    "AuditLogRepository",
    "DashboardRepository",
    # property
    "PropertyProfileRepository",
    "FloorRepository",
    "AmenityRepository",
    "BedTypeRepository",
    "RoomTypeRepository",
    "RoomRepository",
    "TaxRepository",
    "PaymentMethodRepository",
    "CurrencyRepository",
    "SeasonRepository",
    "RatePlanRepository",
    # restaurant
    "RestaurantCategoryRepository",
    "MenuCategoryRepository",
    "KitchenStationRepository",
    "MenuItemRepository",
    "MenuModifierRepository",
    "RestaurantTableRepository",
    # organisation
    "DepartmentRepository",
    "DesignationRepository",
    "GuestIDTypeRepository",
    # settings
    "BusinessSettingsRepository",
]
