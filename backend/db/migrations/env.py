"""
Alembic migration environment — configured for async SQLAlchemy.
Loads DATABASE_URL from .env and uses asyncpg.
"""

import asyncio
from logging.config import fileConfig

from sqlalchemy import pool
from sqlalchemy.ext.asyncio import async_engine_from_config

from alembic import context

# ── Load .env so DATABASE_URL is available ────────────────────
from dotenv import load_dotenv
import os

load_dotenv()  # loads PROJECT2/.env

# ── Import Base + all models so Alembic sees every table ──────
from backend.db.base import Base
import backend.models  # noqa: F401  — triggers model registration

# ── Alembic config ────────────────────────────────────────────
config = context.config

# Override sqlalchemy.url with the value from .env
db_url = os.getenv("DATABASE_URL")
if db_url:
    config.set_main_option("sqlalchemy.url", db_url)

if config.config_file_name is not None and not config.attributes.get("connection"):
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection):
    context.configure(connection=connection, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """Run migrations in 'online' mode with async engine."""
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)
    await connectable.dispose()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    Supports two paths:
    1. Programmatic: a connection is passed via config.attributes["connection"]
       (used by run_migrations() in main.py on startup).
    2. CLI: Alembic creates its own async engine from alembic.ini.
    """
    connectable = config.attributes.get("connection", None)

    if connectable is not None:
        # Already have a sync-wrapped connection — just run migrations on it
        do_run_migrations(connectable)
    else:
        # CLI path — create an async engine and run migrations
        asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()

