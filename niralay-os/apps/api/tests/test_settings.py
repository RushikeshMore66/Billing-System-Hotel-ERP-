"""
Tests for application settings.

Coverage:
  - Default values are sane
  - DATABASE_URL is correctly assembled from parts
  - Environment enum values and properties
  - Constants are correctly typed
  - Security helpers (password hash/verify, token create/decode)
"""

from __future__ import annotations

import pytest

from app.core.environment import Environment
from app.core.settings import get_settings
from app.core.constants import (
    Role,
    Permission,
    ROLE_PERMISSIONS,
    RoomStatus,
    ReservationStatus,
    BillStatus,
    DEFAULT_PAGE_SIZE,
    MAX_PAGE_SIZE,
    DEFAULT_GST_RATE,
)
from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_token,
    create_token_pair,
)


class TestSettings:
    def test_settings_loads(self):
        settings = get_settings()
        assert settings is not None

    def test_app_name(self):
        settings = get_settings()
        assert settings.APP_NAME == "NiralayOS"

    def test_environment_is_testing(self):
        settings = get_settings()
        assert settings.ENVIRONMENT == Environment.TESTING

    def test_database_url_is_set(self):
        settings = get_settings()
        assert settings.DATABASE_URL != ""
        assert "://" in settings.DATABASE_URL

    def test_api_prefix(self):
        settings = get_settings()
        assert settings.API_PREFIX.startswith("/api/")

    def test_token_expire_positive(self):
        settings = get_settings()
        assert settings.ACCESS_TOKEN_EXPIRE_MINUTES > 0
        assert settings.REFRESH_TOKEN_EXPIRE_DAYS > 0

    def test_is_testing_property(self):
        settings = get_settings()
        assert settings.is_testing is True
        assert settings.is_production is False

    def test_allowed_origins_is_list(self):
        settings = get_settings()
        assert isinstance(settings.ALLOWED_ORIGINS, list)


class TestEnvironment:
    def test_environment_values(self):
        assert Environment.DEVELOPMENT.value == "development"
        assert Environment.PRODUCTION.value == "production"
        assert Environment.TESTING.value == "testing"

    def test_is_development(self):
        assert Environment.DEVELOPMENT.is_development is True
        assert Environment.PRODUCTION.is_development is False

    def test_is_production(self):
        assert Environment.PRODUCTION.is_production is True
        assert Environment.DEVELOPMENT.is_production is False

    def test_allows_debug_not_in_production(self):
        assert Environment.PRODUCTION.allows_debug is False
        assert Environment.DEVELOPMENT.allows_debug is True
        assert Environment.TESTING.allows_debug is True

    def test_str_enum_comparison(self):
        """Ensure string enum works with plain strings."""
        assert Environment.DEVELOPMENT == "development"


class TestConstants:
    def test_default_page_size(self):
        assert DEFAULT_PAGE_SIZE > 0
        assert DEFAULT_PAGE_SIZE <= MAX_PAGE_SIZE

    def test_default_gst_rate(self):
        assert DEFAULT_GST_RATE >= 0

    def test_role_enum_values(self):
        roles = [r.value for r in Role]
        assert "super_admin" in roles
        assert "admin" in roles
        assert "receptionist" in roles

    def test_permission_enum_covers_core_domains(self):
        perm_values = {p.value for p in Permission}
        assert "room:view" in perm_values
        assert "reservation:create" in perm_values
        assert "bill:create" in perm_values
        assert "order:create" in perm_values

    def test_super_admin_has_all_permissions(self):
        super_admin_perms = set(ROLE_PERMISSIONS[Role.SUPER_ADMIN])
        all_perms = {p.value for p in Permission}
        assert all_perms == super_admin_perms

    def test_room_statuses_complete(self):
        statuses = {s.value for s in RoomStatus}
        assert "available" in statuses
        assert "occupied" in statuses
        assert "maintenance" in statuses

    def test_reservation_statuses_complete(self):
        statuses = {s.value for s in ReservationStatus}
        assert "pending" in statuses
        assert "confirmed" in statuses
        assert "checked_in" in statuses
        assert "checked_out" in statuses
        assert "cancelled" in statuses

    def test_bill_statuses_complete(self):
        statuses = {s.value for s in BillStatus}
        assert "draft" in statuses
        assert "paid" in statuses
        assert "void" in statuses


class TestPasswordSecurity:
    def test_hash_password_is_not_plain(self):
        plain = "SecurePass123!"
        hashed = hash_password(plain)
        assert hashed != plain

    def test_hash_password_is_bcrypt(self):
        hashed = hash_password("password")
        assert hashed.startswith("$2b$") or hashed.startswith("$2a$")

    def test_verify_password_correct(self):
        plain = "SecurePass123!"
        hashed = hash_password(plain)
        assert verify_password(plain, hashed) is True

    def test_verify_password_wrong(self):
        hashed = hash_password("correctpassword")
        assert verify_password("wrongpassword", hashed) is False

    def test_two_hashes_of_same_password_differ(self):
        """bcrypt uses random salt — same password gives different hashes."""
        h1 = hash_password("same_password")
        h2 = hash_password("same_password")
        assert h1 != h2


class TestJWT:
    _SUBJECT = "00000000-0000-0000-0000-000000000001"
    _ROLE = Role.ADMIN.value
    _PERMS = [Permission.DASHBOARD_VIEW.value, Permission.ROOM_VIEW.value]

    def test_create_access_token_returns_string(self):
        token = create_access_token(self._SUBJECT, self._ROLE, self._PERMS)
        assert isinstance(token, str)
        assert len(token) > 0

    def test_decode_access_token(self):
        token = create_access_token(self._SUBJECT, self._ROLE, self._PERMS)
        payload = decode_token(token)
        assert payload.sub == self._SUBJECT
        assert payload.role == self._ROLE
        assert payload.refresh is False

    def test_access_token_has_permissions(self):
        token = create_access_token(self._SUBJECT, self._ROLE, self._PERMS)
        payload = decode_token(token)
        assert Permission.DASHBOARD_VIEW.value in payload.permissions

    def test_create_refresh_token(self):
        token = create_refresh_token(self._SUBJECT)
        payload = decode_token(token)
        assert payload.sub == self._SUBJECT
        assert payload.refresh is True

    def test_create_token_pair(self):
        pair = create_token_pair(self._SUBJECT, self._ROLE, self._PERMS)
        assert pair.access_token != ""
        assert pair.refresh_token != ""
        assert pair.token_type == "bearer"
        assert pair.expires_in > 0

    def test_invalid_token_raises(self):
        import jwt
        with pytest.raises(jwt.InvalidTokenError):
            decode_token("this.is.not.a.valid.token")
