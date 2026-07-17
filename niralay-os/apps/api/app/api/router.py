"""
Root API router.

Mounts all versioned sub-routers onto the main application.
New sprint routers are registered here — nowhere else.
"""

from fastapi import APIRouter

from app.core.settings import get_settings
from app.api.v1 import health as health_v1
from app.api.v1.auth import router as auth_router
from app.api.v1.users import router as users_router
from app.api.v1.roles import roles_router, permissions_router
from app.api.v1.dashboard import router as dashboard_router

settings = get_settings()

api_router = APIRouter(prefix=settings.API_PREFIX)

# ---- Sprint 1: Foundation ----
api_router.include_router(health_v1.router)

# ---- Sprint 2: Identity & Access Platform ----
api_router.include_router(auth_router)
api_router.include_router(users_router)
api_router.include_router(roles_router)
api_router.include_router(permissions_router)

# ---- Sprint 2 Module 1: Executive Dashboard ----
api_router.include_router(dashboard_router)

# ---- Sprint 3: Business Modules (placeholder) ----
# api_router.include_router(rooms_router)
# api_router.include_router(reservations_router)
