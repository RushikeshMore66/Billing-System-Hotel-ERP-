"""
Roles and Permissions router for NiralayOS — /api/v1/roles  /api/v1/permissions

Endpoints:
    GET    /roles                        — list roles
    POST   /roles                        — create role
    GET    /roles/{id}                   — get role with permissions
    PATCH  /roles/{id}                   — update role
    POST   /roles/{id}/permissions       — assign permissions to role
    DELETE /roles/{id}/permissions       — revoke permissions from role
    GET    /permissions                  — list permissions
    POST   /permissions                  — create permission
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_db, get_current_active_user, require_permission
from app.models.user import User
from app.schemas.base import PaginatedResponse, SuccessResponse
from app.schemas.role import (
    AssignPermissionsRequest,
    PermissionCreate,
    PermissionOut,
    RoleCreate,
    RoleOut,
    RoleUpdate,
    RoleWithPermissions,
)
from app.services.role import RoleService, PermissionService

roles_router = APIRouter(prefix="/roles", tags=["Roles & Permissions"])
permissions_router = APIRouter(prefix="/permissions", tags=["Roles & Permissions"])


# ---------------------------------------------------------------------------
# Roles
# ---------------------------------------------------------------------------
@roles_router.get(
    "",
    response_model=PaginatedResponse[RoleOut],
    status_code=status.HTTP_200_OK,
    summary="List all roles",
)
def list_roles(
    db: Session = Depends(get_db),
    _: User = Depends(get_current_active_user),
) -> PaginatedResponse[RoleOut]:
    svc = RoleService(db)
    roles, total = svc.list(skip=0, limit=100)
    items = [RoleOut.model_validate(r) for r in roles]
    return PaginatedResponse.build(items=items, total=total, page=1, size=100)


@roles_router.post(
    "",
    response_model=SuccessResponse[RoleWithPermissions],
    status_code=status.HTTP_201_CREATED,
    summary="Create a new role",
    description="Requires `settings:manage` permission.",
)
def create_role(
    body: RoleCreate,
    db: Session = Depends(get_db),
    _: User = Depends(require_permission("settings:manage")),
) -> SuccessResponse[RoleWithPermissions]:
    svc = RoleService(db)
    role = svc.create(data=body)
    return SuccessResponse.of(data=RoleWithPermissions.model_validate(role), message="Role created")


@roles_router.get(
    "/{role_id}",
    response_model=SuccessResponse[RoleWithPermissions],
    status_code=status.HTTP_200_OK,
    summary="Get role with its permissions",
)
def get_role(
    role_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_active_user),
) -> SuccessResponse[RoleWithPermissions]:
    svc = RoleService(db)
    role = svc.get_by_id(role_id)
    return SuccessResponse.of(data=RoleWithPermissions.model_validate(role))


@roles_router.patch(
    "/{role_id}",
    response_model=SuccessResponse[RoleWithPermissions],
    status_code=status.HTTP_200_OK,
    summary="Update a role",
)
def update_role(
    role_id: int,
    body: RoleUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(require_permission("settings:manage")),
) -> SuccessResponse[RoleWithPermissions]:
    svc = RoleService(db)
    role = svc.update(role_id=role_id, data=body)
    return SuccessResponse.of(data=RoleWithPermissions.model_validate(role), message="Role updated")


@roles_router.post(
    "/{role_id}/permissions",
    response_model=SuccessResponse[RoleWithPermissions],
    status_code=status.HTTP_200_OK,
    summary="Assign permissions to a role",
)
def assign_permissions(
    role_id: int,
    body: AssignPermissionsRequest,
    db: Session = Depends(get_db),
    _: User = Depends(require_permission("settings:manage")),
) -> SuccessResponse[RoleWithPermissions]:
    svc = RoleService(db)
    role = svc.assign_permissions(role_id=role_id, permission_ids=body.permission_ids)
    return SuccessResponse.of(data=RoleWithPermissions.model_validate(role), message="Permissions assigned")


@roles_router.delete(
    "/{role_id}/permissions",
    response_model=SuccessResponse[RoleWithPermissions],
    status_code=status.HTTP_200_OK,
    summary="Revoke permissions from a role",
)
def revoke_permissions(
    role_id: int,
    body: AssignPermissionsRequest,
    db: Session = Depends(get_db),
    _: User = Depends(require_permission("settings:manage")),
) -> SuccessResponse[RoleWithPermissions]:
    svc = RoleService(db)
    role = svc.revoke_permissions(role_id=role_id, permission_ids=body.permission_ids)
    return SuccessResponse.of(data=RoleWithPermissions.model_validate(role), message="Permissions revoked")


# ---------------------------------------------------------------------------
# Permissions
# ---------------------------------------------------------------------------
@permissions_router.get(
    "",
    response_model=PaginatedResponse[PermissionOut],
    status_code=status.HTTP_200_OK,
    summary="List all permissions",
)
def list_permissions(
    db: Session = Depends(get_db),
    _: User = Depends(get_current_active_user),
) -> PaginatedResponse[PermissionOut]:
    svc = PermissionService(db)
    perms, total = svc.list(skip=0, limit=500)
    items = [PermissionOut.model_validate(p) for p in perms]
    return PaginatedResponse.build(items=items, total=total, page=1, size=500)


@permissions_router.post(
    "",
    response_model=SuccessResponse[PermissionOut],
    status_code=status.HTTP_201_CREATED,
    summary="Create a new permission",
    description="Requires `settings:manage` permission.",
)
def create_permission(
    body: PermissionCreate,
    db: Session = Depends(get_db),
    _: User = Depends(require_permission("settings:manage")),
) -> SuccessResponse[PermissionOut]:
    svc = PermissionService(db)
    perm = svc.create(data=body)
    return SuccessResponse.of(data=PermissionOut.model_validate(perm), message="Permission created")
