"""Rewrite generator.py files to embed cases instead of importing seed modules."""

from __future__ import annotations

import asyncio
import importlib
import re
from pathlib import Path

import yaml

from backend.problem_bank.loader import list_package_dirs
from backend.tools.migrate_seeds_to_packages import (
    _BUILDER_NAMES,
    _generator_source_embedded,
    collect_problem_specs,
)

_HANDCRAFTED = {
    "3sum",
    "two-sum",
    "valid-palindrome",
    "jump-game",
    "valid-anagram",
    "merge-intervals",
    "maximum-subarray",
    "container-with-most-water",
}


def _load_hidden_cases(module_name: str, builder_name: str) -> list[dict]:
    module = importlib.import_module(f"backend.scripts.{module_name}")
    if builder_name and builder_name != "_" and hasattr(module, builder_name):
        builder = getattr(module, builder_name)
        return [case for case in builder() if not case.get("is_sample")]
    for name in _BUILDER_NAMES:
        if hasattr(module, name):
            builder = getattr(module, name)
            return [case for case in builder() if not case.get("is_sample")]
    specs = asyncio.run(collect_problem_specs(module_name))
    if specs:
        return [case for case in specs[0][2] if not case.get("is_sample")]
    raise RuntimeError(f"no cases for {module_name}")


def main() -> None:
    problems_dir = Path(__file__).resolve().parents[2] / "problems"
    fixed = 0
    for package_dir in list_package_dirs(problems_dir):
        if package_dir.name in _HANDCRAFTED:
            continue
        generator_path = package_dir / "generator.py"
        if not generator_path.is_file():
            continue
        text = generator_path.read_text(encoding="utf-8")
        if "cases = [" in text:
            continue

        meta_path = package_dir / "meta.yaml"
        meta = yaml.safe_load(meta_path.read_text(encoding="utf-8"))
        generator_cfg = meta.get("generator") or {}
        count = int(generator_cfg.get("count", 0))
        if count <= 0:
            continue

        match = re.search(r"from backend\.scripts\.(\w+) import (\w+)", text)
        if not match:
            print(f"SKIP {package_dir.name}: cannot resolve legacy builder")
            continue

        module_name, builder_name = match.group(1), match.group(2)
        try:
            hidden = _load_hidden_cases(module_name, builder_name)
        except Exception as exc:
            print(f"SKIP {package_dir.name}: {exc}")
            continue
        fixed_count = len(list((package_dir / "tests").glob("*.in")))
        generated = hidden[fixed_count : fixed_count + count]

        generator_path.write_text(
            _generator_source_embedded(generated),
            encoding="utf-8",
        )
        fixed += 1
        print(f"fixed {package_dir.name} ({len(generated)} cases)")

    print(f"\nDone. Fixed {fixed} generator(s).")


if __name__ == "__main__":
    main()
