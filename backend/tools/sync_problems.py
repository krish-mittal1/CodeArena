"""
CLI: sync version-controlled problem packages into PostgreSQL.

Usage:
    python -m backend.tools.sync_problems --all
    python -m backend.tools.sync_problems --slug two-sum
    python -m backend.tools.sync_problems --all --dry-run
"""

from __future__ import annotations

import argparse
import asyncio
import logging
import sys

from backend.problem_bank.loader import DEFAULT_PROBLEMS_DIR
from backend.problem_bank.sync import sync_all_packages


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Sync problem packages from problems/ into the database.",
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Sync every package under problems/ (default when no slug given)",
    )
    parser.add_argument(
        "--slug",
        type=str,
        default=None,
        help="Sync a single package by folder name (e.g. two-sum)",
    )
    parser.add_argument(
        "--problems-dir",
        type=str,
        default=str(DEFAULT_PROBLEMS_DIR),
        help=f"Root directory for problem packages (default: {DEFAULT_PROBLEMS_DIR})",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate packages without writing to the database",
    )
    return parser


async def _main_async(args: argparse.Namespace) -> int:
    if not args.slug and not args.all:
        args.all = True

    results = await sync_all_packages(
        problems_dir=args.problems_dir,
        slug=args.slug,
        dry_run=args.dry_run,
    )

    if not results:
        logging.error("No packages synced.")
        return 1

    for result in results:
        print(
            f"  {result.slug}: {result.title} — "
            f"{result.test_case_count} cases ({result.created_or_updated})"
        )
    print(f"\nDone. Synced {len(results)} package(s).")
    return 0


def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )
    parser = _build_parser()
    args = parser.parse_args()
    try:
        raise SystemExit(asyncio.run(_main_async(args)))
    except FileNotFoundError as exc:
        logging.error("%s", exc)
        raise SystemExit(1) from exc


if __name__ == "__main__":
    main()
