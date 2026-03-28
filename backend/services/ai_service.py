"""
AI Code Analysis Service — uses Google Gemini to analyze submitted code.
"""

import json
import logging
from typing import Optional

from backend.config import settings

logger = logging.getLogger(__name__)

_SYSTEM_PROMPT = """You are an expert competitive programming mentor and code reviewer.
Analyze the submitted code and return a JSON object with EXACTLY these keys:

{
  "verdict_explanation": "string — clear 2-3 sentence explanation of why the code passed or failed",
  "time_complexity": "string — Big-O of submitted code e.g. O(n log n)",
  "space_complexity": "string — Big-O space usage e.g. O(n)",
  "issues": ["list of strings — each is a specific issue/bug found, empty list [] if accepted"],
  "failed_test_explanation": "string — if wrong answer/TLE/error, explain exactly what happened on the failing case; empty string if accepted",
  "optimized_approach": "string — concise explanation of the best approach/algorithm for this problem",
  "optimized_time_complexity": "string — Big-O of the optimized approach",
  "optimized_space_complexity": "string — Big-O space of the optimized approach",
  "improved_code": "string — clean, fully working improved/optimized code in the SAME language as the submission",
  "tips": ["list of 2-3 short actionable tip strings to help the user improve"]
}

Rules:
- Return ONLY valid JSON, no markdown fences, no extra text.
- Do NOT truncate the improved_code field; it must be complete and runnable.
- Be specific, educational, and encouraging.
"""


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
) -> dict:
    """
    Call Gemini to analyze the user's submitted code.
    Returns a structured dict with analysis or a fallback on failure.
    """
    if not settings.gemini_api_key:
        logger.warning("GEMINI_API_KEY not set — returning placeholder analysis")
        return _fallback_analysis(verdict_status)

    try:
        import google.generativeai as genai

        genai.configure(api_key=settings.gemini_api_key)
        model = genai.GenerativeModel(
            model_name="gemini-2.0-flash",
            system_instruction=_SYSTEM_PROMPT,
        )

        # Build context message
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

Analyze the code and return the JSON object as instructed."""

        response = model.generate_content(prompt)
        raw = response.text.strip()

        # Strip any accidental markdown fences
        if raw.startswith("```"):
            raw = raw.split("\n", 1)[1]
            if raw.endswith("```"):
                raw = raw.rsplit("```", 1)[0]

        return json.loads(raw)

    except json.JSONDecodeError as e:
        logger.error(f"Gemini returned invalid JSON: {e}")
        return _fallback_analysis(verdict_status)
    except Exception as e:
        logger.error(f"Gemini API error: {e}")
        return _fallback_analysis(verdict_status)


def _fallback_analysis(verdict_status: str) -> dict:
    """Return a minimal analysis object when Gemini is unavailable."""
    return {
        "verdict_explanation": f"Your submission received verdict: {verdict_status}.",
        "time_complexity": "N/A",
        "space_complexity": "N/A",
        "issues": [],
        "failed_test_explanation": "",
        "optimized_approach": "AI analysis is currently unavailable. Please check back later.",
        "optimized_time_complexity": "N/A",
        "optimized_space_complexity": "N/A",
        "improved_code": "",
        "tips": ["Try to think about edge cases.", "Consider the time complexity.", "Review your algorithm."],
    }
