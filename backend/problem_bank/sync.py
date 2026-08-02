"""
Sync problem packages from disk into PostgreSQL.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from backend.config import settings
from backend.models.problem import Problem
from backend.problem_bank.loader import (
    DEFAULT_PROBLEMS_DIR,
    list_package_dirs,
    load_meta,
    load_test_cases,
    merge_presentation,
    resolve_problems_dir,
)
from backend.problem_bank.upsert import upsert_problem

logger = logging.getLogger(__name__)


@dataclass
class SyncResult:
    slug: str
    title: str
    test_case_count: int
    created_or_updated: str


async def sync_package(
    db: AsyncSession | None,
    package_dir: Path,
    *,
    dry_run: bool = False,
) -> SyncResult:
    meta = load_meta(package_dir)
    cases = load_test_cases(package_dir, meta)
    presentation = merge_presentation(meta, cases)

    if meta.slug != package_dir.name:
        logger.warning(
            "Package folder '%s' does not match meta.slug '%s' — using meta.slug",
            package_dir.name,
            meta.slug,
        )

    if dry_run:
        logger.info(
            "[DRY RUN] Would sync '%s' (%s) with %d test cases",
            meta.title,
            meta.slug,
            len(cases),
        )
        return SyncResult(
            slug=meta.slug,
            title=meta.title,
            test_case_count=len(cases),
            created_or_updated="dry-run",
        )

    existing_before = await db.execute(
        select(Problem.id).where(Problem.title == meta.title)
    )
    had_existing = existing_before.scalar_one_or_none() is not None

    kwargs = meta.to_problem_kwargs()
    kwargs["presentation"] = presentation

    # TestCase model has no explanation column — keep that in presentation.examples
    db_cases = [
        {
            "input": c["input"],
            "expected_output": c["expected_output"],
            "order_index": c["order_index"],
            "is_sample": c["is_sample"],
        }
        for c in cases
    ]

    await upsert_problem(db, meta.title, kwargs, db_cases)

    action = "updated" if had_existing else "created"
    logger.info(
        "Synced '%s' (%s): %d test cases [%s]",
        meta.title,
        meta.slug,
        len(cases),
        action,
    )
    return SyncResult(
        slug=meta.slug,
        title=meta.title,
        test_case_count=len(cases),
        created_or_updated=action,
    )


async def sync_all_packages(
    *,
    problems_dir: Path | str | None = None,
    slug: str | None = None,
    dry_run: bool = False,
) -> list[SyncResult]:
    root = resolve_problems_dir(problems_dir)
    if not root.is_dir():
        raise FileNotFoundError(f"Problems directory not found: {root}")

    package_dirs = list_package_dirs(root)
    if slug:
        package_dirs = [p for p in package_dirs if p.name == slug]
        if not package_dirs:
            raise FileNotFoundError(f"No package with slug '{slug}' under {root}")

    if not package_dirs:
        logger.warning("No problem packages found in %s", root)
        return []

    results: list[SyncResult] = []

    if dry_run:
        for package_dir in package_dirs:
            async with _DryRunSession() as db:
                results.append(await sync_package(db, package_dir, dry_run=True))
        return results

    engine = create_async_engine(settings.database_url, echo=False)
    session_factory = async_sessionmaker(engine, expire_on_commit=False)

    try:
        for package_dir in package_dirs:
            async with session_factory() as db:
                try:
                    result = await sync_package(db, package_dir, dry_run=False)
                    results.append(result)
                except Exception as exc:
                    logger.error(
                        "Failed to sync package '%s': %s",
                        package_dir.name,
                        exc,
                        exc_info=True,
                    )
                    raise
    finally:
        await engine.dispose()

    return results


class _DryRunSession:
    """No-op async session placeholder for dry-run validation."""

    async def __aenter__(self) -> AsyncSession:
        return None  # type: ignore[return-value]

    async def __aexit__(self, *args: object) -> None:
        return None
