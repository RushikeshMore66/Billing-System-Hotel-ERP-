"""
Business settings router for NiralayOS — /api/v1/settings/*

Endpoints:
    GET    /settings/business  — retrieve (or auto-create) singleton settings
    PATCH  /settings/business  — update settings
"""

from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_active_user, get_db, require_permission
from app.models.user import User
from app.schemas.base import SuccessResponse
from app.schemas.business_settings import BusinessSettingsOut, BusinessSettingsUpdate
from app.services.business_settings import BusinessSettingsService

router = APIRouter(prefix="/settings", tags=["Business Settings"])


@router.get(
    "/business",
    response_model=SuccessResponse[BusinessSettingsOut],
    summary="Get business settings",
    description="Returns (or auto-creates) the singleton business settings row.",
)
def get_settings(
    db: Session = Depends(get_db),
    _: User = Depends(require_permission("settings:view")),
) -> SuccessResponse[BusinessSettingsOut]:
    settings = BusinessSettingsService(db).get()
    return SuccessResponse.of(data=BusinessSettingsOut.model_validate(settings))


@router.patch(
    "/business",
    response_model=SuccessResponse[BusinessSettingsOut],
    summary="Update business settings",
    description="Partial update on the singleton business settings row.",
)
def update_settings(
    body: BusinessSettingsUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("settings:manage")),
) -> SuccessResponse[BusinessSettingsOut]:
    settings = BusinessSettingsService(db).update(body, updated_by=str(current_user.uuid))
    return SuccessResponse.of(data=BusinessSettingsOut.model_validate(settings), message="Settings updated")
