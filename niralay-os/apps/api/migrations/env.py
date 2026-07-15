"""
Alembic migration environment.

Reads database URL from application settings so that the same
.env file is used for both the app and migrations.
"""

from __future__ import annotations

import sys
from pathlib import Path

# Make app importable from this directory
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool
from alembic import context

from app.core.settings import get_settings
from app.database.base import Base

# ------------------------------------------------------------------
# Alembic Config object — provides .ini file values
# ------------------------------------------------------------------
config = context.config

# Configure Python logging from the alembic.ini [loggers] section
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Inject the real DATABASE_URL from settings
settings = get_settings()
config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)

# Target metadata for autogenerate
target_metadata = Base.metadata


# ------------------------------------------------------------------
# Migration runners
# ------------------------------------------------------------------
def run_migrations_offline() -> None:
    """
    Run migrations in 'offline' mode.

    Generates SQL to stdout without a live database connection.
    Useful for reviewing or applying migrations manually.
    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
        compare_server_default=True,
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """
    Run migrations in 'online' mode (live DB connection).
    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
            compare_server_default=True,
        )
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
