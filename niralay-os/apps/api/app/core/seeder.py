"""
Database seeder for NiralayOS.

Seeds default roles, permissions, and the bootstrap admin user on application startup.
Idempotent — safe to run multiple times.
"""

from __future__ import annotations

import logging
from sqlalchemy.orm import Session

from app.core.constants import Role as RoleEnum, ROLE_PERMISSIONS, Permission as PermissionEnum
from app.core.settings import get_settings
from app.models.role import Role, Permission
from app.models.user import User
from app.repositories.role import RoleRepository, PermissionRepository
from app.repositories.user import UserRepository
from app.schemas.role import PermissionCreate, RoleCreate
from app.schemas.user import UserCreate
from app.services.role import RoleService, PermissionService
from app.services.user import UserService

logger = logging.getLogger(__name__)


def seed_database(db: Session) -> None:
    """Run all seeders in order."""
    logger.info("Starting database seeder...")
    
    _seed_permissions(db)
    _seed_roles(db)
    _seed_bootstrap_admin(db)
    
    logger.info("Database seeder completed successfully.")


def _seed_permissions(db: Session) -> None:
    """Seed all atomic permissions from constants."""
    repo = PermissionRepository(db)
    svc = PermissionService(db)
    
    for perm_enum in PermissionEnum:
        if not repo.code_exists(perm_enum.value):
            module, action = perm_enum.value.split(":")
            svc.create(PermissionCreate(
                code=perm_enum.value,
                module=module,
                action=action,
                description=f"Can {action} {module}"
            ))


def _seed_roles(db: Session) -> None:
    """Seed default system roles and map their permissions."""
    role_svc = RoleService(db)
    perm_repo = PermissionRepository(db)
    role_repo = RoleRepository(db)
    
    for role_enum, perm_codes in ROLE_PERMISSIONS.items():
        role_slug = role_enum.value
        role_name = role_slug.replace("_", " ").title()
        
        # Create role if missing
        role = role_repo.get_by_slug(role_slug)
        if not role:
            # Find permission IDs for the assigned codes
            perms = perm_repo.get_by_codes(perm_codes)
            perm_ids = [p.id for p in perms]
            
            role = role_svc.create(RoleCreate(
                name=role_name,
                slug=role_slug,
                description=f"System generated {role_name} role",
                permission_ids=perm_ids,
            ))
            # Mark as system role manually since the schema doesn't expose it
            role.is_system = True
            role_repo.save(role)
        else:
            # Ensure permissions are synced (optional, could just leave as-is)
            perms = perm_repo.get_by_codes(perm_codes)
            perm_ids = [p.id for p in perms]
            role_svc.assign_permissions(role.id, perm_ids)


def _seed_bootstrap_admin(db: Session) -> None:
    """Create the superuser if no users exist or admin is missing."""
    cfg = get_settings()
    user_repo = UserRepository(db)
    
    if user_repo.email_exists(cfg.ADMIN_EMAIL):
        return
        
    role_repo = RoleRepository(db)
    super_admin_role = role_repo.get_by_slug(RoleEnum.SUPER_ADMIN.value)
    
    if not super_admin_role:
        logger.error("Super admin role missing, cannot create bootstrap admin.")
        return

    user_svc = UserService(db)
    user = user_svc.create(UserCreate(
        username="admin",
        email=cfg.ADMIN_EMAIL,
        password=cfg.ADMIN_PASSWORD,
        full_name=cfg.ADMIN_FULL_NAME,
        is_superuser=True,
        role_ids=[super_admin_role.id],
    ))
    
    logger.info(f"Bootstrap admin created with email: {cfg.ADMIN_EMAIL}")
