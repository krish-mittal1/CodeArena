"""
Migrate legacy seed_*.py scripts into version-controlled problem packages.

Usage:
    python -m backend.tools.migrate_seeds_to_packages
    python -m backend.tools.migrate_seeds_to_packages --dry-run
    python -m backend.tools.migrate_seeds_to_packages --force
"""

from __future__ import annotations

import argparse
import ast
import importlib
import importlib.util
import logging
import re
import textwrap
import uuid
from enum import Enum
from pathlib import Path
from types import ModuleType
from typing import Any
from unittest.mock import AsyncMock, MagicMock

import yaml

from backend.problem_bank.loader import DEFAULT_PROBLEMS_DIR, list_package_dirs, load_meta

logger = logging.getLogger(__name__)

_REPO_ROOT = Path(__file__).resolve().parents[2]
_SCRIPTS_DIR = _REPO_ROOT / "backend" / "scripts"

_SKIP_MODULES = {
    "seed_bots",
    "seed_company_array_pack",
    "seed_company_binary_search_pack",
    "seed_company_binary_tree_pack",
    "seed_company_greedy_pack",
    "seed_company_linked_list_pack",
    "seed_company_sliding_window_pack",
    "seed_company_string_pack",
    "seed_company_two_pointers_pack",
}

_BUILDER_NAMES = (
    "build_cases",
    "build_test_cases",
    "generate_test_cases",
)

_FIXED_TEST_MAX = 8


def _title_to_slug(title: str) -> str:
    slug = title.lower().replace("'", "").replace("'", "")
    slug = re.sub(r"[^a-z0-9]+", "-", slug).strip("-")
    return slug or "problem"


def _normalize_value(value: Any) -> Any:
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, list):
        return [_normalize_value(item) for item in value]
    if isinstance(value, dict):
        return {key: _normalize_value(val) for key, val in value.items()}
    return value


def _normalize_kwargs(kwargs: dict[str, Any]) -> dict[str, Any]:
    return {key: _normalize_value(val) for key, val in kwargs.items()}


def _existing_titles(problems_dir: Path) -> dict[str, str]:
    """Map problem title -> slug for packages that already exist."""
    mapping: dict[str, str] = {}
    for package_dir in list_package_dirs(problems_dir):
        meta = load_meta(package_dir)
        mapping[meta.title] = meta.slug
    return mapping


def _load_seed_module(module_name: str) -> ModuleType:
    return importlib.import_module(f"backend.scripts.{module_name}")


def _find_case_builder(module: ModuleType):
    for name in _BUILDER_NAMES:
        builder = getattr(module, name, None)
        if callable(builder):
            return builder
    return None


def _extract_from_problems_list(module: ModuleType) -> list[tuple[str, dict, list[dict], str]]:
    problems = getattr(module, "PROBLEMS", None)
    if not isinstance(problems, list):
        return []

    specs: list[tuple[str, dict, list[dict], str]] = []
    for item in problems:
        if isinstance(item, dict):
            title = item["title"]
            kwargs = _normalize_kwargs(item["kwargs"])
            builder = item["builder"]
            builder_name = builder.__name__ if callable(builder) else "build_cases"
            cases = builder() if callable(builder) else list(builder)
            specs.append((title, kwargs, cases, builder_name))
        elif isinstance(item, (tuple, list)) and len(item) == 3:
            title, builder, kwargs = item
            builder_name = builder.__name__ if callable(builder) else "build_cases"
            cases = builder() if callable(builder) else list(builder)
            specs.append((title, _normalize_kwargs(kwargs), cases, builder_name))
    return specs


def _extract_kwargs_from_ast(module_name: str) -> dict[str, Any] | None:
    """Best-effort parse of kwargs dict passed to upsert_problem or assigned to problem_data."""
    path = _SCRIPTS_DIR / f"{module_name}.py"
    source = path.read_text(encoding="utf-8")
    tree = ast.parse(source)

    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        func = node.func
        func_name = getattr(func, "id", None) or getattr(func, "attr", None)
        if func_name != "upsert_problem":
            continue
        if len(node.args) < 3:
            continue
        kwargs_node = node.args[2]
        try:
            return _normalize_kwargs(ast.literal_eval(kwargs_node))
        except (ValueError, SyntaxError):
            continue

    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            for target in node.targets:
                name = getattr(target, "id", None)
                if name not in {"problem_data", "kwargs"}:
                    continue
                try:
                    value = ast.literal_eval(node.value)
                except (ValueError, SyntaxError):
                    continue
                if isinstance(value, dict) and "description" in value:
                    return _normalize_kwargs(value)
    return None


def _extract_title_from_ast(module_name: str) -> str | None:
    path = _SCRIPTS_DIR / f"{module_name}.py"
    source = path.read_text(encoding="utf-8")
    tree = ast.parse(source)

    for node in tree.body:
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if getattr(target, "id", None) == "TITLE":
                    try:
                        value = ast.literal_eval(node.value)
                    except (ValueError, SyntaxError):
                        continue
                    if isinstance(value, str):
                        return value

    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if getattr(target, "id", None) != "title":
                    continue
                try:
                    value = ast.literal_eval(node.value)
                except (ValueError, SyntaxError):
                    continue
                if isinstance(value, str):
                    return value
    return None


def _patch_module_sqlalchemy(module: ModuleType, session: _CaptureSession) -> dict[str, Any]:
    """Patch sqlalchemy helpers on the loaded seed module namespace."""
    originals: dict[str, Any] = {}

    def session_factory(*_args, **_kwargs):
        def _maker():
            return session

        return _maker

    mock_engine = MagicMock()
    mock_engine.dispose = AsyncMock(return_value=None)

    for name, replacement in (
        ("create_async_engine", lambda *_a, **_k: mock_engine),
        ("async_sessionmaker", session_factory),
    ):
        if hasattr(module, name):
            originals[name] = getattr(module, name)
            setattr(module, name, replacement)
    return originals


def _restore_module_sqlalchemy(module: ModuleType, originals: dict[str, Any]) -> None:
    for name, value in originals.items():
        setattr(module, name, value)


class _CaptureSession:
    def __init__(self) -> None:
        self.specs: list[tuple[str, dict, list[dict]]] = []
        self._problem: Any | None = None
        self._cases: list[dict] = []

    def add(self, obj: Any) -> None:
        from backend.models.problem import Problem
        from backend.models.test_case import TestCase

        if isinstance(obj, Problem):
            self._flush()
            self._problem = obj
        elif isinstance(obj, TestCase):
            self._cases.append(
                {
                    "input": obj.input,
                    "expected_output": obj.expected_output,
                    "is_sample": obj.is_sample,
                    "order_index": obj.order_index,
                }
            )

    def _flush(self) -> None:
        if self._problem is None:
            return
        kwargs = {
            key: getattr(self._problem, key)
            for key in (
                "description",
                "difficulty",
                "input_format",
                "output_format",
                "constraints",
                "problem_type",
                "rating",
                "time_limit_ms",
                "memory_limit_mb",
                "method_name",
                "parameters",
                "return_type",
                "is_active",
            )
            if hasattr(self._problem, key) and getattr(self._problem, key) is not None
        }
        self.specs.append((self._problem.title, _normalize_kwargs(kwargs), list(self._cases)))
        self._problem = None
        self._cases = []

    async def execute(self, *_args, **_kwargs):
        result = MagicMock()
        result.scalars.return_value = result
        result.scalar_one_or_none.return_value = None
        result.scalar_one.return_value = None
        result.first.return_value = None
        result.all.return_value = []
        return result

    async def commit(self) -> None:
        self._flush()

    async def flush(self) -> None:
        pass

    async def refresh(self, *_args, **_kwargs) -> None:
        pass

    async def rollback(self) -> None:
        pass

    async def delete(self, *_args, **_kwargs) -> None:
        pass

    async def __aenter__(self) -> _CaptureSession:
        return self

    async def __aexit__(self, *_args) -> None:
        self._flush()


async def _mock_upsert(_db, title: str, kwargs: dict, cases) -> MagicMock:
    _mock_upsert.captured.append((title, _normalize_kwargs(kwargs), list(cases)))
    mock = MagicMock()
    mock.id = uuid.uuid4()
    return mock


_mock_upsert.captured = []


def _patch_upsert_targets() -> list[tuple[ModuleType, Any]]:
    restored: list[tuple[ModuleType, Any]] = []
    targets = [
        "backend.problem_bank.upsert",
        "backend.scripts.array_seed_utils",
        "backend.scripts.string_seed_utils",
        "backend.scripts.linked_list_seed_utils",
        "backend.scripts.binary_search_seed_utils",
    ]
    for target in targets:
        try:
            mod = importlib.import_module(target)
        except ImportError:
            continue
        if hasattr(mod, "upsert_problem"):
            restored.append((mod, mod.upsert_problem))
            mod.upsert_problem = _mock_upsert
    return restored


def _restore_upsert_targets(restored: list[tuple[ModuleType, Any]]) -> None:
    for mod, original in restored:
        mod.upsert_problem = original


async def _extract_via_seed(module: ModuleType, module_name: str) -> list[tuple[str, dict, list[dict], str]]:
    if not hasattr(module, "seed"):
        return []

    _mock_upsert.captured = []
    restored = _patch_upsert_targets()
    session = _CaptureSession()
    module_sqlalchemy = _patch_module_sqlalchemy(module, session)
    builder_name = getattr(_find_case_builder(module), "__name__", "build_cases")

    try:
        await module.seed()
    finally:
        _restore_module_sqlalchemy(module, module_sqlalchemy)
        _restore_upsert_targets(restored)

    specs: list[tuple[str, dict, list[dict], str]] = []
    for title, kwargs, cases in _mock_upsert.captured:
        specs.append((title, kwargs, cases, builder_name))
    for title, kwargs, cases in session.specs:
        specs.append((title, kwargs, cases, builder_name))
    return specs


def _extract_direct_builder_specs(
    module: ModuleType, module_name: str
) -> list[tuple[str, dict, list[dict], str]]:
    builder = _find_case_builder(module)
    if builder is None:
        return []

    title = getattr(module, "TITLE", None) or _extract_title_from_ast(module_name)
    kwargs = _extract_kwargs_from_ast(module_name)
    if not title or not kwargs:
        return []

    return [(title, kwargs, builder(), builder.__name__)]


async def collect_problem_specs(module_name: str) -> list[tuple[str, dict, list[dict], str]]:
    module = _load_seed_module(module_name)

    specs = _extract_from_problems_list(module)
    if specs:
        return specs

    specs = await _extract_via_seed(module, module_name)
    if specs:
        return specs

    return _extract_direct_builder_specs(module, module_name)


def _infer_problem_type(kwargs: dict) -> str:
    if kwargs.get("method_name"):
        return "dsa"
    return kwargs.get("problem_type", "cp")


def _meta_yaml(slug: str, title: str, kwargs: dict, generator_count: int, seed: int) -> str:
    meta: dict[str, Any] = {
        "slug": slug,
        "title": title,
        "problem_type": _infer_problem_type(kwargs),
        "difficulty": kwargs.get("difficulty", "medium"),
        "rating": kwargs.get("rating", 1000),
        "description": kwargs.get("description", title),
        "input_format": kwargs.get("input_format", ""),
        "output_format": kwargs.get("output_format", ""),
        "time_limit_ms": kwargs.get("time_limit_ms", 2000),
        "memory_limit_mb": kwargs.get("memory_limit_mb", 256),
        "is_active": kwargs.get("is_active", True),
    }
    if kwargs.get("constraints"):
        meta["constraints"] = kwargs["constraints"]
    if meta["problem_type"] == "dsa":
        meta["method_name"] = kwargs.get("method_name")
        meta["parameters"] = kwargs.get("parameters")
        meta["return_type"] = kwargs.get("return_type")
    if generator_count > 0:
        meta["generator"] = {"count": generator_count, "seed": seed}
    return yaml.safe_dump(meta, sort_keys=False, allow_unicode=True)


def _write_case_files(directory: Path, cases: list[dict], start_index: int = 0) -> int:
    directory.mkdir(parents=True, exist_ok=True)
    for offset, case in enumerate(cases):
        stem = f"{start_index + offset + 1:02d}"
        (directory / f"{stem}.in").write_text(case["input"] + "\n", encoding="utf-8")
        (directory / f"{stem}.out").write_text(case["expected_output"] + "\n", encoding="utf-8")
    return len(cases)


def _generator_source_embedded(generated_cases: list[dict]) -> str:
    lines = [
        '"""Auto-migrated bulk hidden test cases."""',
        "",
        "def generate_cases(*, count: int, seed: int, start_index: int):",
        "    del seed",
        "    cases = [",
    ]
    for case in generated_cases:
        inp = repr(case["input"])
        out = repr(case["expected_output"])
        lines.append(f"        {{'input': {inp}, 'expected_output': {out}}},")
    lines.extend(
        [
            "    ]",
            "    for offset, case in enumerate(cases[:count]):",
            "        yield {",
            '            "input": case["input"],',
            '            "expected_output": case["expected_output"],',
            '            "order_index": start_index + offset,',
            '            "is_sample": False,',
            "        }",
        ]
    )
    return "\n".join(lines) + "\n"


def write_package(
    *,
    problems_dir: Path,
    slug: str,
    title: str,
    kwargs: dict,
    cases: list[dict],
    module_name: str,
    builder_name: str,
    dry_run: bool = False,
) -> Path:
    package_dir = problems_dir / slug
    samples = [case for case in cases if case.get("is_sample")]
    hidden = [case for case in cases if not case.get("is_sample")]

    if len(hidden) <= 15:
        fixed_hidden = hidden
        generated_hidden: list[dict] = []
        generator_count = 0
    else:
        fixed_hidden = hidden[:_FIXED_TEST_MAX]
        generated_hidden = hidden[_FIXED_TEST_MAX:]
        generator_count = len(generated_hidden)

    seed = sum(ord(ch) for ch in title) % 10_000_000

    if dry_run:
        logger.info(
            "[DRY RUN] Would write %s (%s): %d samples, %d fixed tests, %d generated",
            title,
            slug,
            len(samples),
            len(fixed_hidden),
            generator_count,
        )
        return package_dir

    if package_dir.exists():
        import shutil

        shutil.rmtree(package_dir)

    package_dir.mkdir(parents=True)
    (package_dir / "meta.yaml").write_text(
        _meta_yaml(slug, title, kwargs, generator_count, seed),
        encoding="utf-8",
    )
    _write_case_files(package_dir / "samples", samples)
    _write_case_files(package_dir / "tests", fixed_hidden)
    if generator_count > 0:
        (package_dir / "generator.py").write_text(
            _generator_source_embedded(generated_hidden),
            encoding="utf-8",
        )
    return package_dir


def _allocate_slug(title: str, problems_dir: Path, existing: dict[str, str]) -> str:
    if title in existing:
        return existing[title]
    base = _title_to_slug(title)
    slug = base
    suffix = 2
    while (problems_dir / slug).exists():
        slug = f"{base}-{suffix}"
        suffix += 1
    return slug


async def migrate_all(
    *,
    problems_dir: Path,
    dry_run: bool = False,
    force: bool = False,
) -> list[Path]:
    existing_titles = _existing_titles(problems_dir)
    written: list[Path] = []
    errors: list[str] = []

    seed_files = sorted(_SCRIPTS_DIR.glob("seed_*.py"))
    for path in seed_files:
        module_name = path.stem
        if module_name in _SKIP_MODULES:
            continue

        try:
            specs = await collect_problem_specs(module_name)
        except Exception as exc:
            errors.append(f"{module_name}: {exc}")
            logger.exception("Failed to extract %s", module_name)
            continue

        if not specs:
            logger.warning("No problems extracted from %s", module_name)
            continue

        for title, kwargs, cases, builder_name in specs:
            if title in existing_titles and not force:
                logger.info("Skipping existing package for %r", title)
                continue
            slug = _allocate_slug(title, problems_dir, existing_titles)
            package_dir = write_package(
                problems_dir=problems_dir,
                slug=slug,
                title=title,
                kwargs=kwargs,
                cases=cases,
                module_name=module_name,
                builder_name=builder_name,
                dry_run=dry_run,
            )
            written.append(package_dir)
            existing_titles[title] = slug

    if errors:
        logger.error("Migration finished with %d error(s):", len(errors))
        for err in errors:
            logger.error("  %s", err)

    return written


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Migrate legacy seed scripts to problem packages.")
    parser.add_argument("--dry-run", action="store_true", help="Report actions without writing files")
    parser.add_argument("--force", action="store_true", help="Overwrite packages for titles already present")
    parser.add_argument(
        "--problems-dir",
        type=str,
        default=str(DEFAULT_PROBLEMS_DIR),
        help="Destination problems directory",
    )
    return parser


async def _main_async(args: argparse.Namespace) -> int:
    written = await migrate_all(
        problems_dir=Path(args.problems_dir),
        dry_run=args.dry_run,
        force=args.force,
    )
    action = "Would create" if args.dry_run else "Created"
    print(f"\n{action} {len(written)} package(s).")
    return 0 if written or args.dry_run else 1


def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )
    parser = _build_parser()
    args = parser.parse_args()
    raise SystemExit(__import__("asyncio").run(_main_async(args)))


if __name__ == "__main__":
    main()
