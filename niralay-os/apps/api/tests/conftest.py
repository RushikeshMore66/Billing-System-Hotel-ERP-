"""
Pytest configuration and shared fixtures for NiralayOS API tests.

Provides:
  - Override settings to use TESTING environment and in-memory SQLite
  - TestClient fixture
  - Isolated database per test session
"""

from __future__ import annotations

import os
from typing import Generator
import pytest

# Override environment BEFORE importing the app, so settings load with test values
os.environ.setdefault("ENVIRONMENT", "testing")
os.environ.setdefault("DATABASE_URL", "sqlite:///./test.db")
os.environ.setdefault("SECRET_KEY", "test_secret_key_for_testing_only_min_32_chars!")
os.environ.setdefault("LOG_FORMAT", "text")
os.environ.setdefault("LOG_LEVEL", "WARNING")

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database.base import Base
from app.database.session import get_db
from app.main import app


# ---------------------------------------------------------------------------
# In-memory SQLite for tests (no PostgreSQL required)
# ---------------------------------------------------------------------------
TEST_DATABASE_URL = "sqlite:///./test_niralayos.db"

_test_engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
)
_TestingSessionLocal = sessionmaker(
    bind=_test_engine,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
)


def override_get_db():
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
    """Create all tables in the test database once per session."""
    Base.metadata.create_all(bind=_test_engine)
    yield
    Base.metadata.drop_all(bind=_test_engine)


@pytest.fixture(scope="session")
def client() -> Generator[TestClient, None, None]:
    """
    Shared test client for the entire test session.

    Overrides the DB dependency to use the in-memory SQLite database.
    """
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app, raise_server_exceptions=True) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture()
def db():
    """Provide a database session for a single test (auto-rollback)."""
    connection = _test_engine.connect()
    transaction = connection.begin()
    session = _TestingSessionLocal(bind=connection)
    yield session
    session.close()
    transaction.rollback()
    connection.close()
