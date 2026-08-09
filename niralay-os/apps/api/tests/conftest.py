"""
Pytest configuration and shared fixtures for NiralayOS API tests.

Provides:
  - Override settings to use TESTING environment and in-memory SQLite
  - TestClient fixture
  - Isolated database per test function
"""

from __future__ import annotations

import os
from typing import Generator
import pytest
from app.models.user import User
from app.core.security import create_access_token

# Override environment BEFORE importing the app so settings load with test values
os.environ["ENVIRONMENT"] = "testing"
os.environ["DATABASE_URL"] = "sqlite:///./test_niralayos.db"
os.environ.setdefault("SECRET_KEY", "test_secret_key_for_testing_only_min_32_chars!")
os.environ.setdefault("LOG_FORMAT", "text")
os.environ.setdefault("LOG_LEVEL", "WARNING")

# Clear the settings lru_cache so the overridden env vars take effect
from app.core.settings import get_settings
get_settings.cache_clear()

from fastapi.testclient import TestClient  # noqa: E402
from sqlalchemy import create_engine  # noqa: E402
from sqlalchemy.orm import sessionmaker, Session  # noqa: E402

from app.database.base import Base  # noqa: E402
from app.database.session import get_db  # noqa: E402
import app.database.health as _health_mod  # noqa: E402
import app.database.session as _session_mod  # noqa: E402


# ---------------------------------------------------------------------------
# Shared SQLite engine for the entire test session
#
# Uses in-memory SQLite with StaticPool so all connections share the same
# in-memory database.  No stale files, no index-already-exists errors.
# ---------------------------------------------------------------------------
from sqlalchemy.pool import StaticPool

TEST_DATABASE_URL = "sqlite://"

_test_engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
_TestingSessionLocal = sessionmaker(
    bind=_test_engine,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
)


def override_get_db() -> Generator[Session, None, None]:
    """FastAPI dependency override — yields a SQLite session."""
    db = _TestingSessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------
@pytest.fixture(scope="session", autouse=True)
def create_test_tables():
    """Create all tables in the SQLite test database once per session.

    The stale DB file was already deleted at module import time, so
    create_all() always starts from a blank slate.
    """
    Base.metadata.create_all(bind=_test_engine)
    yield
    Base.metadata.drop_all(bind=_test_engine)



@pytest.fixture(scope="session")
def client() -> Generator[TestClient, None, None]:
    """
    Session-scoped unauthenticated TestClient.

    Patches health check and session factory so the lifespan startup
    does not attempt a real PostgreSQL connection.
    """
    from unittest.mock import patch
    from app.main import app

    async def _fake_health():
        return True, "ok (sqlite test)"

    app.dependency_overrides[get_db] = override_get_db

    with patch.object(_health_mod, "check_database_health", _fake_health), \
         patch.object(_session_mod, "get_session_factory", lambda: _TestingSessionLocal):
        with TestClient(app, raise_server_exceptions=True) as c:
            yield c

    app.dependency_overrides.clear()


@pytest.fixture()
def db() -> Generator[Session, None, None]:
    """Provide a database session for a single test (rolls back on completion)."""
    connection = _test_engine.connect()
    transaction = connection.begin()
    # SQLAlchemy 2.x: bind session to a specific connection
    session = _TestingSessionLocal(bind=connection)

    # Seed roles/permissions so service layer tests have valid data
    from app.core.seeder import seed_database
    seed_database(session)
    session.commit()

    yield session

    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture(scope="session")
def superuser(client: TestClient) -> User:
    """
    Session-scoped superuser fixture.

    Depends on `client` (which starts the app and seeds the DB via lifespan).
    Looks up the seeded admin user from the persistent test SQLite DB.
    """
    from app.repositories.user import UserRepository
    db = _TestingSessionLocal()
    try:
        user_repo = UserRepository(db)
        user = user_repo.get_by_email("admin@niralayos.com")
        if not user:
            raise RuntimeError(
                "Bootstrap admin user not found in test DB. "
                "Ensure the seeder ran during lifespan startup."
            )
        return user
    finally:
        db.close()


@pytest.fixture(scope="session")
def superuser_client(client: TestClient, superuser: User) -> TestClient:
    """
    Session-scoped authenticated TestClient running as the superuser.

    Adds the Authorization header to the shared session-scoped client.
    Tests that need unauthenticated access must override or use `client`
    with headers explicitly cleared.
    """
    token = create_access_token(
        subject=str(superuser.uuid),
        role="super_admin",
        permissions=["*"],
    )
    client.headers.update({"Authorization": f"Bearer {token}"})
    return client
