"""
AI Code Analysis Service — Groq or Google Gemini via unified LLM client.
"""

import json
import logging
import re
from collections import OrderedDict
from dataclasses import dataclass
from typing import Any, Optional

from backend.services.llm_client import call_json_llm, llm_provider, parse_llm_json

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class AnalyzeCodeResult:
    """Outcome of analyze_code — quota should tick only when used_llm is True."""

    analysis: dict
    from_cache: bool = False
    used_llm: bool = False


_SYSTEM_PROMPT = """You are an expert interview coach for competitive programming.
Give short, structured feedback a learner can scan in under a minute.
Warm, direct, concrete. No buzzwords. No essay paragraphs.

Return ONLY a JSON object with EXACTLY these keys:

{
  "verdict_summary": "string — 1 to 2 short sentences. Pass/fail in plain language and the main takeaway.",
  "root_cause": "string — If failed: the specific bug or wrong idea (1 to 3 sentences). If accepted: why the approach is correct (1 to 2 sentences). Empty string only if truly nothing to say.",
  "time_complexity": "string — Big-O time complexity of THEIR submitted code, e.g. O(N) or O(N log N)",
  "space_complexity": "string — Big-O space complexity of THEIR submitted code, e.g. O(1) or O(N)",
  "optimal_time_complexity": "string — Best possible / optimal Big-O time complexity for this problem, e.g. O(N)",
  "optimal_space_complexity": "string — Best possible / optimal Big-O space complexity for this problem, e.g. O(1)",
  "key_insight": "string — The core correct idea / pattern in 2 to 4 sentences. Name the pattern if classic (two pointers, sliding window, binary search, etc.). Do NOT dump a full editorial.",
  "fix_hints": ["string — 2 to 5 short coaching steps. Hint at the fix; do NOT paste a full solution walkthrough. Interview-coach tone: guide, don't spoil every line."],
  "edge_cases": ["string — 0 to 4 concrete edge cases they missed or should re-check. Empty list [] if none."],
  "improved_code": "string — Optional clean reference solution in the SAME language. Include ONLY when it clearly helps (failed submission, or accepted but messy). Otherwise return empty string \"\". Must be complete and runnable when non-empty.",
  "tips": ["string — 2 to 3 short reusable takeaways for similar problems."]
}

Rules:
- Return ONLY valid JSON. No markdown fences. No prose outside JSON.
- Prefer short sentences. No walls of text. No repeated explanations across fields.
- fix_hints are coaching nudges, not a line-by-line rewrite of the solution.
- If accepted and code is already clean, improved_code may be \"\".
- If the code failed a test, root_cause must connect the bug to the failure when possible.
- Always fill time_complexity and space_complexity for the submitted code (use \"N/A\" only if truly unknowable).
"""

_AI_CACHE_MAX = 256

# Section headers the model sometimes emits when JSON fails
_SECTION_ALIASES = {
    "verdict_summary": ("verdict summary", "verdict", "summary"),
    "root_cause": ("root cause", "what's wrong", "what is wrong", "bug", "failure reason"),
    "time_complexity": ("time complexity", "time"),
    "space_complexity": ("space complexity", "space"),
    "key_insight": ("key insight", "correct approach", "insight", "approach"),
    "fix_hints": ("fix hints", "hints", "steps", "step-by-step", "how to fix"),
    "edge_cases": ("edge cases", "edge case", "missed cases"),
    "improved_code": ("improved code", "reference solution", "code", "solution"),
    "tips": ("tips", "takeaways", "remember"),
}


class _LRUCache(OrderedDict):
    def get_cache(self, key):
        if key in self:
            self.move_to_end(key)
            return self[key]
        return None

    def set_cache(self, key, value):
        self[key] = value
        self.move_to_end(key)
        while len(self) > _AI_CACHE_MAX:
            self.popitem(last=False)


AI_CACHE = _LRUCache()


def has_cached_analysis(submission_id: Optional[str]) -> bool:
    """True if analyze_code would return a cache hit for this submission_id."""
    if not submission_id:
        return False
    return AI_CACHE.get_cache(submission_id) is not None


def _as_str(value: Any, default: str = "") -> str:
    if value is None:
        return default
    if isinstance(value, str):
        return value.strip()
    if isinstance(value, (int, float)):
        return str(value)
    return default


def _as_str_list(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, str):
        text = value.strip()
        if not text:
            return []
        # Split numbered / bulleted lines into list items when the model returns a blob
        lines = re.split(r"\n+", text)
        items = []
        for line in lines:
            cleaned = re.sub(r"^[\s\-\*\d\.\)\(]+", "", line).strip()
            if cleaned:
                items.append(cleaned)
        return items if len(items) > 1 else [text]
    if isinstance(value, list):
        out = []
        for item in value:
            if isinstance(item, str) and item.strip():
                out.append(item.strip())
            elif isinstance(item, dict):
                # legacy alternative approach objects
                summary = _as_str(item.get("summary") or item.get("name"))
                if summary:
                    out.append(summary)
        return out
    return []


def _join_paragraphs(*parts: str) -> str:
    return "\n\n".join(p.strip() for p in parts if p and p.strip())


def _parse_prose_sections(raw: str) -> Optional[dict]:
    """Best-effort parse of labeled prose when the model ignores JSON mode."""
    text = (raw or "").strip()
    if not text:
        return None

    # Strip outer fences
    if text.startswith("```"):
        text = re.sub(r"^```(?:json|text)?\s*", "", text, flags=re.IGNORECASE)
        text = re.sub(r"\s*```$", "", text).strip()

    # Prefer JSON slice if present
    start = text.find("{")
    end = text.rfind("}")
    if start >= 0 and end > start:
        try:
            parsed = json.loads(text[start : end + 1])
            if isinstance(parsed, dict):
                return parsed
        except json.JSONDecodeError:
            pass

    header_re = re.compile(
        r"(?im)^\s*(?:#{1,3}\s*)?(?:\*\*)?([A-Za-z][A-Za-z0-9 dual/\-]{1,40})(?:\*\*)?\s*:?\s*$"
    )
    matches = list(header_re.finditer(text))
    if not matches:
        # Single prose blob → treat as verdict + insight
        first = text.split("\n\n")[0].strip()[:400]
        return {
            "verdict_summary": first,
            "root_cause": "",
            "key_insight": text[:800],
            "fix_hints": [],
            "edge_cases": [],
            "tips": [],
            "improved_code": "",
            "time_complexity": "N/A",
            "space_complexity": "N/A",
        }

    sections: dict[str, str] = {}
    for i, match in enumerate(matches):
        label = match.group(1).strip().lower()
        body_start = match.end()
        body_end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        body = text[body_start:body_end].strip()
        sections[label] = body

    result: dict[str, Any] = {}
    for field, aliases in _SECTION_ALIASES.items():
        for alias in aliases:
            for label, body in sections.items():
                if label == alias or label.startswith(alias):
                    result[field] = body
                    break
            if field in result:
                break

    if not result:
        return None
    return result


def _normalize_analysis_result(result: dict, verdict_status: str) -> dict:
    """
    Normalize new or legacy LLM payloads into one stable shape for the UI.

    Preferred fields (new):
      verdict_summary, root_cause, time/space_complexity, key_insight,
      fix_hints, edge_cases, improved_code, tips

    Legacy fields are filled for older clients / insights list compatibility.
    """
    if not isinstance(result, dict):
        return _fallback_analysis(verdict_status, "Invalid AI response format")

    # --- Preferred fields (accept new names, fall back to legacy) ---
    verdict_summary = _as_str(
        result.get("verdict_summary")
        or result.get("verdict_explanation")
    )
    if not verdict_summary:
        verdict_summary = f"Submission verdict: {verdict_status}."

    root_cause = _as_str(result.get("root_cause"))
    if not root_cause:
        issues = _as_str_list(result.get("issues"))
        failed = _as_str(result.get("failed_test_explanation"))
        if issues:
            root_cause = issues[0]
        elif failed:
            root_cause = failed

    time_complexity = _as_str(result.get("time_complexity"), "N/A") or "N/A"
    space_complexity = _as_str(result.get("space_complexity"), "N/A") or "N/A"

    key_insight = _as_str(
        result.get("key_insight")
        or result.get("optimized_approach")
        or result.get("problem_concept")
    )
    if not key_insight:
        key_insight = "Focus on the core pattern for this problem, then check the edge cases that usually break naive solutions."

    fix_hints = _as_str_list(result.get("fix_hints"))
    if not fix_hints:
        # Derive coaching steps from legacy optimized_approach paragraphs
        optimized = _as_str(result.get("optimized_approach"))
        if optimized:
            chunks = [c.strip() for c in re.split(r"\n+|(?<=\.)\s+(?=[A-Z0-9])", optimized) if c.strip()]
            fix_hints = chunks[:5]
        elif _as_str_list(result.get("tips")):
            fix_hints = _as_str_list(result.get("tips"))[:3]

    edge_cases = _as_str_list(result.get("edge_cases"))
    improved_code = _as_str(result.get("improved_code"))
    tips = _as_str_list(result.get("tips"))
    if not tips and fix_hints:
        tips = fix_hints[:2]

    # Issues: prefer explicit list, else root_cause as single issue when failed-ish
    issues = _as_str_list(result.get("issues"))
    if not issues and root_cause and str(verdict_status).lower() not in ("accepted", "ac"):
        issues = [root_cause]

    failed_test_explanation = _as_str(result.get("failed_test_explanation"))
    submitted_approach = _as_str(result.get("submitted_approach")) or verdict_summary
    problem_concept = _as_str(result.get("problem_concept")) or key_insight
    optimized_approach = _as_str(result.get("optimized_approach")) or _join_paragraphs(
        key_insight, "\n".join(f"{i + 1}. {h}" for i, h in enumerate(fix_hints))
    )
    worst_approach = _as_str(result.get("worst_approach")) or (
        "Start from the direct brute-force idea, then remove repeated work."
    )

    alternatives = result.get("alternative_approaches")
    if not isinstance(alternatives, list):
        alternatives = []
    normalized_alternatives = []
    for index, item in enumerate(alternatives):
        if isinstance(item, str) and item.strip():
            normalized_alternatives.append(
                {
                    "name": f"Alternative {index + 1}",
                    "summary": item.strip(),
                    "time_complexity": "N/A",
                    "space_complexity": "N/A",
                    "when_to_use": "",
                }
            )
        elif isinstance(item, dict):
            normalized_alternatives.append(
                {
                    "name": _as_str(item.get("name")) or f"Alternative {index + 1}",
                    "summary": _as_str(item.get("summary")),
                    "time_complexity": _as_str(item.get("time_complexity"), "N/A") or "N/A",
                    "space_complexity": _as_str(item.get("space_complexity"), "N/A") or "N/A",
                    "when_to_use": _as_str(item.get("when_to_use")),
                }
            )

    opt_time = (
        _as_str(result.get("optimal_time_complexity"))
        or _as_str(result.get("optimized_time_complexity"))
        or "N/A"
    )
    opt_space = (
        _as_str(result.get("optimal_space_complexity"))
        or _as_str(result.get("optimized_space_complexity"))
        or "N/A"
    )

    return {
        # Preferred (UI primary)
        "verdict_summary": verdict_summary,
        "root_cause": root_cause,
        "time_complexity": time_complexity,
        "space_complexity": space_complexity,
        "optimal_time_complexity": opt_time,
        "optimal_space_complexity": opt_space,
        "key_insight": key_insight,
        "fix_hints": fix_hints,
        "edge_cases": edge_cases,
        "improved_code": improved_code,
        "tips": tips,
        # Legacy aliases (insights list, older UI, mock debrief)
        "verdict_explanation": verdict_summary if not root_cause else _join_paragraphs(verdict_summary, root_cause),
        "submitted_approach": submitted_approach,
        "problem_concept": problem_concept,
        "issues": issues,
        "failed_test_explanation": failed_test_explanation,
        "optimized_approach": optimized_approach,
        "optimized_time_complexity": _as_str(result.get("optimized_time_complexity"), "N/A") or "N/A",
        "optimized_space_complexity": _as_str(result.get("optimized_space_complexity"), "N/A") or "N/A",
        "worst_approach": worst_approach,
        "worst_time_complexity": _as_str(result.get("worst_time_complexity"), "N/A") or "N/A",
        "worst_space_complexity": _as_str(result.get("worst_space_complexity"), "N/A") or "N/A",
        "alternative_approaches": normalized_alternatives,
    }


async def analyze_code(
    problem_title: str,
    problem_description: str,
    constraints: Optional[str],
    language: str,
    code: str,
    verdict_status: str,
    failed_input: Optional[str] = None,
    expected_output: Optional[str] = None,
    actual_output: Optional[str] = None,
    error_output: Optional[str] = None,
    submission_id: Optional[str] = None,
) -> AnalyzeCodeResult:
    """
    Call Groq/Gemini to analyze submitted code.

    Returns AnalyzeCodeResult. Callers must only consume analysis quota when
    ``used_llm`` is True (not cache hits, not fallback/error placeholders).
    """
    if submission_id:
        cached = AI_CACHE.get_cache(submission_id)
        if cached is not None:
            logger.info("Returning cached AI analysis for submission %s", submission_id)
            return AnalyzeCodeResult(
                analysis=_normalize_analysis_result(cached, verdict_status),
                from_cache=True,
                used_llm=False,
            )

    if not llm_provider():
        logger.warning("GROQ_API_KEY / GEMINI_API_KEY not set - returning placeholder analysis")
        return AnalyzeCodeResult(
            analysis=_fallback_analysis(
                verdict_status,
                "AI API key missing. Add GROQ_API_KEY or GEMINI_API_KEY to .env",
            ),
            from_cache=False,
            used_llm=False,
        )

    failed_section = ""
    if failed_input:
        failed_section = f"""
Failed Test Case:
  Input: {failed_input}
  Expected Output: {expected_output or 'N/A'}
  Actual Output: {actual_output or 'N/A'}
  Error Output: {error_output or 'N/A'}
"""

    prompt = f"""Problem: {problem_title}

Description:
{problem_description}

Constraints:
{constraints or 'Not specified'}

Language: {language}

Submitted Code:
```{language}
{code}
```

Verdict: {verdict_status}
{failed_section}

Respond with the JSON object only. Keep every string field short and scannable.
Coach with hints; do not write a textbook chapter."""

    max_retries = 3
    last_error = ""

    for attempt in range(max_retries):
        try:
            logger.info(
                "Calling %s for '%s' (Attempt %d/%d)...",
                llm_provider(),
                problem_title,
                attempt + 1,
                max_retries,
            )

            raw = await call_json_llm(
                system=_SYSTEM_PROMPT,
                user=prompt,
                max_tokens=3072,
            )

            parsed: Any = None
            try:
                parsed = parse_llm_json(raw)
            except json.JSONDecodeError:
                parsed = _parse_prose_sections(raw)
                if parsed is None:
                    raise

            if not isinstance(parsed, dict):
                raise json.JSONDecodeError("Expected JSON object", str(parsed), 0)

            result = _normalize_analysis_result(parsed, verdict_status)

            if submission_id:
                AI_CACHE.set_cache(submission_id, result)

            logger.info("AI analysis complete for '%s'", problem_title)
            return AnalyzeCodeResult(
                analysis=result,
                from_cache=False,
                used_llm=True,
            )

        except json.JSONDecodeError as e:
            last_error = f"Invalid JSON: {e}"
            logger.error("LLM returned invalid JSON (attempt %d): %s", attempt + 1, e)
            if attempt < max_retries - 1:
                import asyncio
                await asyncio.sleep((attempt + 1) * 2)
                continue
            return AnalyzeCodeResult(
                analysis=_fallback_analysis(verdict_status, "Invalid AI response format"),
                from_cache=False,
                used_llm=False,
            )
        except Exception as e:
            last_error = str(e)
            logger.error("LLM API error (attempt %d): %s", attempt + 1, last_error)
            if attempt < max_retries - 1:
                import asyncio
                await asyncio.sleep((attempt + 1) * 2)
                continue

    logger.error("All %d LLM API attempts failed: %s", max_retries, last_error)
    return AnalyzeCodeResult(
        analysis=_fallback_analysis(verdict_status, f"AI Error: {last_error[:60]}"),
        from_cache=False,
        used_llm=False,
    )


def _fallback_analysis(verdict_status: str, error_reason: str = "AI analysis is currently unavailable") -> dict:
    """Return a minimal analysis object when AI is unavailable."""
    summary = f"Your submission received verdict: {verdict_status}."
    insight = f"{error_reason}. Check server configuration and API keys, then try again."
    tips = [
        "Test small edge cases first.",
        "Check the time complexity before submitting.",
        "Compare your approach with the common pattern for this problem type.",
    ]
    return _normalize_analysis_result(
        {
            "verdict_summary": summary,
            "root_cause": "A full AI explanation is not available right now.",
            "time_complexity": "N/A",
            "space_complexity": "N/A",
            "key_insight": insight,
            "fix_hints": [
                "Re-read the failing case and walk the code by hand.",
                "Check off-by-one and empty-input edge cases.",
                "Retry analysis once the API key is configured.",
            ],
            "edge_cases": [],
            "improved_code": "",
            "tips": tips,
        },
        verdict_status,
    )
