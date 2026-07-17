"""
Users router for NiralayOS — /api/v1/users/*

Endpoints:
    GET    /users          — list users (requires user:view)
    POST   /users          — create user (requires user:create)
    GET    /users/{id}     — get user detail (requires user:view)
    PATCH  /users/{id}     — update user (requires user:update)
    DELETE /users/{id}     — deactivate user (requires user:delete)
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_db, get_current_active_user, require_permission
from app.models.user import User
from app.schemas.base import PaginatedResponse, SuccessResponse
from app.schemas.auth import MessageResponse
from app.schemas.user import UserCreate, UserListOut, UserOut, UserUpdate
from app.services.user import UserService

router = APIRouter(prefix="/users", tags=["Users"])


@router.get(
    "",
    response_model=PaginatedResponse[UserListOut],
    status_code=status.HTTP_200_OK,
    summary="List users",
    description="Returns a paginated list of active users. Requires `user:view` permission.",
)
def list_users(
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(20, ge=1, le=200, description="Items per page"),
    search: str | None = Query(None, description="Search by name, email, or username"),
    db: Session = Depends(get_db),
    _: User = Depends(require_permission("user:view")),
) -> PaginatedResponse[UserListOut]:
    svc = UserService(db)
    offset = (page - 1) * size
    users, total = svc.list(skip=offset, limit=size, search=search)
    items = [UserListOut.model_validate(u) for u in users]
    return PaginatedResponse.build(items=items, total=total, page=page, size=size)


@router.post(
    "",
    response_model=SuccessResponse[UserOut],
    status_code=status.HTTP_201_CREATED,
    summary="Create a new user",
    description="Creates a user with password hashing and optional role assignment. Requires `user:create`.",
)
def create_user(
    body: UserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("user:create")),
) -> SuccessResponse[UserOut]:
    svc = UserService(db)
    user = svc.create(data=body, created_by=str(current_user.uuid))
    return SuccessResponse.of(data=UserOut.model_validate(user), message="User created successfully")


@router.get(
    "/{user_id}",
    response_model=SuccessResponse[UserOut],
    status_code=status.HTTP_200_OK,
    summary="Get user by ID",
)
def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_permission("user:view")),
) -> SuccessResponse[UserOut]:
    svc = UserService(db)
    user = svc.get_by_id(user_id)
    return SuccessResponse.of(data=UserOut.model_validate(user))


@router.patch(
    "/{user_id}",
    response_model=SuccessResponse[UserOut],
    status_code=status.HTTP_200_OK,
    summary="Update a user",
    description="Partial update. Requires `user:update`.",
)
def update_user(
    user_id: int,
    body: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("user:update")),
) -> SuccessResponse[UserOut]:
    svc = UserService(db)
    user = svc.update(user_id=user_id, data=body, updated_by=str(current_user.uuid))
    return SuccessResponse.of(data=UserOut.model_validate(user), message="User updated")


@router.delete(
    "/{user_id}",
    response_model=SuccessResponse[MessageResponse],
    status_code=status.HTTP_200_OK,
    summary="Deactivate a user",
    description="Soft-deletes the user record. Requires `user:delete`.",
)
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("user:delete")),
) -> SuccessResponse[MessageResponse]:
    svc = UserService(db)
    svc.deactivate(user_id=user_id, deleted_by=str(current_user.uuid))
    return SuccessResponse.of(data=MessageResponse(message="User deactivated"))
