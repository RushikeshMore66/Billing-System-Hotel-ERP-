"""
Root API router.

Mounts all versioned sub-routers onto the main application.
New sprint routers are registered here — nowhere else.
"""

from fastapi import APIRouter

from app.core.settings import get_settings
from app.api.v1 import health as health_v1

settings = get_settings()

api_router = APIRouter(prefix=settings.API_PREFIX)

# ---- Sprint 1: Foundation ----
api_router.include_router(health_v1.router)

# ---- Sprint 2: Authentication (placeholder, filled in Sprint 2) ----
# api_router.include_router(auth_router)

# ---- Sprint 3: Dashboard (placeholder) ----
# api_router.include_router(dashboard_router)
