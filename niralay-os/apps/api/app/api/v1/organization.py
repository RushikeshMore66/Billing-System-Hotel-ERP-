"""
Organisation configuration router for NiralayOS — /api/v1/organization/*

Endpoints:
    GET/POST/PATCH/DELETE  /organization/departments
    GET/POST/PATCH/DELETE  /organization/designations
    GET/POST/PATCH/DELETE  /organization/guest-id-types
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_active_user, get_db, require_permission
from app.models.user import User
from app.schemas.auth import MessageResponse
from app.schemas.base import PaginatedResponse, SuccessResponse
from app.schemas.organization import (
    DepartmentCreate,
    DepartmentOut,
    DepartmentUpdate,
    DesignationCreate,
    DesignationOut,
    DesignationUpdate,
    GuestIDTypeCreate,
    GuestIDTypeOut,
    GuestIDTypeUpdate,
)
from app.services.organization import DepartmentService, DesignationService, GuestIDTypeService

router = APIRouter(prefix="/organization", tags=["Organisation Configuration"])


# ===========================================================================
# Departments
# ===========================================================================
@router.get(
    "/departments",
    response_model=PaginatedResponse[DepartmentOut],
    summary="List departments",
)
def list_departments(
    page: int = Query(1, ge=1),
    size: int = Query(50, ge=1, le=200),
    search: str | None = Query(None),
    db: Session = Depends(get_db),
    _: User = Depends(require_permission("organization:view")),
) -> PaginatedResponse[DepartmentOut]:
    items, total = DepartmentService(db).list(skip=(page - 1) * size, limit=size, search=search)
    return PaginatedResponse.build(items=[DepartmentOut.model_validate(d) for d in items], total=total, page=page, size=size)


@router.post(
    "/departments",
    response_model=SuccessResponse[DepartmentOut],
    status_code=status.HTTP_201_CREATED,
    summary="Create department",
)
def create_department(
    body: DepartmentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("organization:manage")),
) -> SuccessResponse[DepartmentOut]:
    d = DepartmentService(db).create(body, created_by=str(current_user.uuid))
    return SuccessResponse.of(data=DepartmentOut.model_validate(d), message="Department created")


@router.patch(
    "/departments/{dept_id}",
    response_model=SuccessResponse[DepartmentOut],
    summary="Update department",
)
def update_department(
    dept_id: int,
    body: DepartmentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("organization:manage")),
) -> SuccessResponse[DepartmentOut]:
    d = DepartmentService(db).update(dept_id, body, updated_by=str(current_user.uuid))
    return SuccessResponse.of(data=DepartmentOut.model_validate(d), message="Department updated")


@router.delete(
    "/departments/{dept_id}",
    response_model=SuccessResponse[MessageResponse],
    summary="Delete department",
)
def delete_department(
    dept_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("organization:manage")),
) -> SuccessResponse[MessageResponse]:
    DepartmentService(db).delete(dept_id, deleted_by=str(current_user.uuid))
    return SuccessResponse.of(data=MessageResponse(message="Department deleted"))


# ===========================================================================
# Designations
# ===========================================================================
@router.get(
    "/designations",
    response_model=PaginatedResponse[DesignationOut],
    summary="List designations",
)
def list_designations(
    page: int = Query(1, ge=1),
    size: int = Query(200, ge=1, le=500),
    search: str | None = Query(None),
    department_id: int | None = Query(None),
    db: Session = Depends(get_db),
    _: User = Depends(require_permission("organization:view")),
) -> PaginatedResponse[DesignationOut]:
    items, total = DesignationService(db).list(
        skip=(page - 1) * size, limit=size, search=search, department_id=department_id
    )
    return PaginatedResponse.build(items=[DesignationOut.model_validate(d) for d in items], total=total, page=page, size=size)


@router.post(
    "/designations",
    response_model=SuccessResponse[DesignationOut],
    status_code=status.HTTP_201_CREATED,
    summary="Create designation",
)
def create_designation(
    body: DesignationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("organization:manage")),
) -> SuccessResponse[DesignationOut]:
    d = DesignationService(db).create(body, created_by=str(current_user.uuid))
    return SuccessResponse.of(data=DesignationOut.model_validate(d), message="Designation created")


@router.patch(
    "/designations/{desig_id}",
    response_model=SuccessResponse[DesignationOut],
    summary="Update designation",
)
def update_designation(
    desig_id: int,
    body: DesignationUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("organization:manage")),
) -> SuccessResponse[DesignationOut]:
    d = DesignationService(db).update(desig_id, body, updated_by=str(current_user.uuid))
    return SuccessResponse.of(data=DesignationOut.model_validate(d), message="Designation updated")


@router.delete(
    "/designations/{desig_id}",
    response_model=SuccessResponse[MessageResponse],
    summary="Delete designation",
)
def delete_designation(
    desig_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("organization:manage")),
) -> SuccessResponse[MessageResponse]:
    DesignationService(db).delete(desig_id, deleted_by=str(current_user.uuid))
    return SuccessResponse.of(data=MessageResponse(message="Designation deleted"))


# ===========================================================================
# Guest ID Types
# ===========================================================================
@router.get(
    "/guest-id-types",
    response_model=PaginatedResponse[GuestIDTypeOut],
    summary="List guest ID types",
)
def list_guest_id_types(
    page: int = Query(1, ge=1),
    size: int = Query(50, ge=1, le=200),
    search: str | None = Query(None),
    db: Session = Depends(get_db),
    _: User = Depends(require_permission("organization:view")),
) -> PaginatedResponse[GuestIDTypeOut]:
    items, total = GuestIDTypeService(db).list(skip=(page - 1) * size, limit=size, search=search)
    return PaginatedResponse.build(items=[GuestIDTypeOut.model_validate(g) for g in items], total=total, page=page, size=size)


@router.post(
    "/guest-id-types",
    response_model=SuccessResponse[GuestIDTypeOut],
    status_code=status.HTTP_201_CREATED,
    summary="Create guest ID type",
)
def create_guest_id_type(
    body: GuestIDTypeCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("organization:manage")),
) -> SuccessResponse[GuestIDTypeOut]:
    g = GuestIDTypeService(db).create(body, created_by=str(current_user.uuid))
    return SuccessResponse.of(data=GuestIDTypeOut.model_validate(g), message="Guest ID type created")


@router.patch(
    "/guest-id-types/{id_type_id}",
    response_model=SuccessResponse[GuestIDTypeOut],
    summary="Update guest ID type",
)
def update_guest_id_type(
    id_type_id: int,
    body: GuestIDTypeUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("organization:manage")),
) -> SuccessResponse[GuestIDTypeOut]:
    g = GuestIDTypeService(db).update(id_type_id, body, updated_by=str(current_user.uuid))
    return SuccessResponse.of(data=GuestIDTypeOut.model_validate(g), message="Guest ID type updated")


@router.delete(
    "/guest-id-types/{id_type_id}",
    response_model=SuccessResponse[MessageResponse],
    summary="Delete guest ID type",
)
def delete_guest_id_type(
    id_type_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("organization:manage")),
) -> SuccessResponse[MessageResponse]:
    GuestIDTypeService(db).delete(id_type_id, deleted_by=str(current_user.uuid))
    return SuccessResponse.of(data=MessageResponse(message="Guest ID type deleted"))
