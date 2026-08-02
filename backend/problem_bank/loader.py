"""
Load problem packages from the problems/ directory at the repo root.
"""

from __future__ import annotations

import importlib.util
import json
import logging
import re
from pathlib import Path
from typing import Iterator

import yaml

from backend.problem_bank.schema import GeneratorConfig, ProblemPackageMeta

logger = logging.getLogger(__name__)

_REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_PROBLEMS_DIR = _REPO_ROOT / "problems"

_PAIR_PATTERN = re.compile(r"^(.+)\.(in|out)$")


def resolve_problems_dir(explicit: str | Path | None = None) -> Path:
    if explicit is not None:
        return Path(explicit).resolve()
    return DEFAULT_PROBLEMS_DIR


def list_package_dirs(problems_dir: Path) -> list[Path]:
    if not problems_dir.is_dir():
        return []
    return sorted(
        p for p in problems_dir.iterdir()
        if p.is_dir() and (p / "meta.yaml").is_file()
    )


def load_meta(package_dir: Path) -> ProblemPackageMeta:
    meta_path = package_dir / "meta.yaml"
    with open(meta_path, encoding="utf-8") as f:
        raw = yaml.safe_load(f)
    if not isinstance(raw, dict):
        raise ValueError(f"{meta_path}: expected a YAML mapping")
    return ProblemPackageMeta.model_validate(raw)


def _natural_sort_key(path: Path) -> list:
    parts = re.split(r"(\d+)", path.stem)
    return [int(p) if p.isdigit() else p.lower() for p in parts]


def _normalize_case_payload(
    *,
    input_text: str,
    expected_output: str,
    order_index: int,
    is_sample: bool,
    explanation: str | None = None,
) -> dict:
    case = {
        "input": input_text.rstrip("\n"),
        "expected_output": expected_output.rstrip("\n"),
        "order_index": order_index,
        "is_sample": is_sample,
    }
    if explanation:
        case["explanation"] = explanation.strip()
    return case


def _load_json_sample_cases(directory: Path, start_index: int) -> list[dict]:
    """Optional LeetCode-style samples/*.json with {input, output, explanation?}."""
    if not directory.is_dir():
        return []

    cases: list[dict] = []
    json_files = sorted(
        [p for p in directory.iterdir() if p.is_file() and p.suffix == ".json"],
        key=_natural_sort_key,
    )
    for order, file_path in enumerate(json_files):
        try:
            raw = json.loads(file_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            raise ValueError(f"Invalid JSON sample {file_path}: {exc}") from exc
        if not isinstance(raw, dict):
            raise ValueError(f"{file_path}: expected a JSON object")
        if "input" not in raw or ("output" not in raw and "expected_output" not in raw):
            raise ValueError(
                f"{file_path}: needs 'input' and 'output' (or 'expected_output')"
            )
        input_val = raw["input"]
        output_val = raw.get("output", raw.get("expected_output"))
        if not isinstance(input_val, str):
            input_val = (
                "\n".join(json.dumps(line) if not isinstance(line, str) else line for line in input_val)
                if isinstance(input_val, list)
                else json.dumps(input_val)
            )
        if not isinstance(output_val, str):
            output_val = json.dumps(output_val)
        explanation = raw.get("explanation")
        cases.append(
            _normalize_case_payload(
                input_text=str(input_val),
                expected_output=str(output_val),
                order_index=start_index + order,
                is_sample=True,
                explanation=str(explanation) if explanation else None,
            )
        )
    return cases


def _load_paired_cases(directory: Path, *, is_sample: bool, start_index: int) -> list[dict]:
    if not directory.is_dir():
        return []

    stems: dict[str, dict[str, Path]] = {}
    for file_path in directory.iterdir():
        if not file_path.is_file():
            continue
        if file_path.suffix == ".json":
            continue
        if file_path.name.endswith(".explanation.txt"):
            continue
        match = _PAIR_PATTERN.match(file_path.name)
        if not match:
            logger.warning("Skipping unrecognized file in %s: %s", directory, file_path.name)
            continue
        stem, suffix = match.group(1), match.group(2)
        stems.setdefault(stem, {})[suffix] = file_path

    cases: list[dict] = []
    order = 0
    for stem in sorted(stems.keys(), key=lambda s: _natural_sort_key(Path(s))):
        pair = stems[stem]
        if "in" not in pair or "out" not in pair:
            raise ValueError(
                f"Incomplete test pair in {directory}: stem '{stem}' "
                f"(need both .in and .out)"
            )
        explanation = None
        explanation_path = directory / f"{stem}.explanation.txt"
        if explanation_path.is_file():
            explanation = explanation_path.read_text(encoding="utf-8")
        cases.append(
            _normalize_case_payload(
                input_text=pair["in"].read_text(encoding="utf-8"),
                expected_output=pair["out"].read_text(encoding="utf-8"),
                order_index=start_index + order,
                is_sample=is_sample,
                explanation=explanation,
            )
        )
        order += 1
    return cases


def _load_generator_cases(
    package_dir: Path,
    generator_cfg: GeneratorConfig,
    start_index: int,
) -> list[dict]:
    generator_path = package_dir / "generator.py"
    if generator_cfg.count <= 0:
        return []
    if not generator_path.is_file():
        raise FileNotFoundError(
            f"{package_dir.name}: generator.count={generator_cfg.count} "
            f"but {generator_path.name} is missing"
        )

    spec = importlib.util.spec_from_file_location(
        f"problem_generator_{package_dir.name}",
        generator_path,
    )
    if spec is None or spec.loader is None:
        raise ImportError(f"Could not load generator module: {generator_path}")

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    if not hasattr(module, "generate_cases"):
        raise AttributeError(
            f"{generator_path}: must define generate_cases(count, seed, start_index)"
        )

    raw_cases = module.generate_cases(
        count=generator_cfg.count,
        seed=generator_cfg.seed,
        start_index=start_index,
    )

    cases: list[dict] = []
    if isinstance(raw_cases, dict):
        raw_iter: Iterator[dict] = iter([raw_cases])
    else:
        raw_iter = iter(raw_cases)

    for item in raw_iter:
        if not isinstance(item, dict):
            raise TypeError(f"{generator_path}: generate_cases() must yield dicts")
        if "input" not in item or "expected_output" not in item:
            raise ValueError(
                f"{generator_path}: each case needs 'input' and 'expected_output'"
            )
        cases.append(
            {
                "input": str(item["input"]),
                "expected_output": str(item["expected_output"]),
                "order_index": int(item.get("order_index", start_index + len(cases))),
                "is_sample": bool(item.get("is_sample", False)),
            }
        )
    return cases


def load_test_cases(package_dir: Path, meta: ProblemPackageMeta) -> list[dict]:
    """Load sample files, hidden test files, and optional generator output."""
    cases: list[dict] = []
    samples_dir = package_dir / "samples"
    json_samples = _load_json_sample_cases(samples_dir, start_index=0)
    paired_samples = _load_paired_cases(samples_dir, is_sample=True, start_index=0)

    if json_samples and paired_samples:
        logger.info(
            "%s: using %d JSON sample(s); ignoring paired .in/.out samples",
            package_dir.name,
            len(json_samples),
        )
        cases.extend(json_samples)
    elif json_samples:
        cases.extend(json_samples)
    else:
        cases.extend(paired_samples)

    cases.extend(
        _load_paired_cases(
            package_dir / "tests",
            is_sample=False,
            start_index=len(cases),
        )
    )
    if meta.generator:
        cases.extend(
            _load_generator_cases(package_dir, meta.generator, start_index=len(cases))
        )

    if not cases:
        raise ValueError(
            f"{package_dir.name}: no test cases found "
            f"(add samples/, tests/, or generator config)"
        )

    for idx, case in enumerate(cases):
        case["order_index"] = idx

    return cases


def merge_presentation(meta: ProblemPackageMeta, cases: list[dict]) -> dict | None:
    """
    Build final presentation payload for DB.

    Sample I/O always comes from sample cases; meta.examples may add explanations
    or override display I/O. Images come from meta.images.
    """
    sample_cases = [c for c in cases if c.get("is_sample")]
    meta_examples = meta.examples or []

    examples: list[dict] = []
    for idx, sample in enumerate(sample_cases):
        overlay = meta_examples[idx] if idx < len(meta_examples) else None
        explanation = None
        if overlay and overlay.explanation:
            explanation = overlay.explanation
        elif sample.get("explanation"):
            explanation = sample["explanation"]

        examples.append(
            {
                "input": (overlay.input if overlay and overlay.input else sample["input"]),
                "output": (
                    overlay.output
                    if overlay and overlay.output
                    else sample["expected_output"]
                ),
                **({"explanation": explanation} if explanation else {}),
            }
        )

    for overlay in meta_examples[len(sample_cases) :]:
        if not overlay.input and not overlay.output:
            continue
        entry: dict = {
            "input": overlay.input or "",
            "output": overlay.output or "",
        }
        if overlay.explanation:
            entry["explanation"] = overlay.explanation
        examples.append(entry)

    images = [img.model_dump() for img in meta.images] if meta.images else []

    if not examples and not images:
        return None

    payload: dict = {}
    if examples:
        payload["examples"] = examples
    if images:
        payload["images"] = images
    return payload
