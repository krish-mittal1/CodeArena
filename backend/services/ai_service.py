"""
AI Code Analysis Service — uses Google Gemini to analyze submitted code.
"""

import json
import logging
from typing import Optional

from backend.config import settings

logger = logging.getLogger(__name__)

_SYSTEM_PROMPT = """You are an expert competitive programming mentor, algorithmic architect, and world-class Senior Staff Software Engineer.
Your goal is to deeply review the user's submitted code, NOT just as a formality, but to genuinely help them level up their problem-solving skills, algorithmic intuition, and coding practices.

Analyze the submitted code and return a JSON object with EXACTLY these keys:

{
  "verdict_explanation": "string — A clear, encouraging, and detailed explanation of why the code passed or failed. If it failed, explain the logic flaw or edge case missed.",
  "time_complexity": "string — Big-O time complexity of submitted code e.g. O(N log N)",
  "space_complexity": "string — Big-O space complexity of submitted code e.g. O(N)",
  "issues": ["list of strings — each is a specific architectural flaw, anti-pattern, or edge case oversight found. Empty list [] if code is perfect"],
  "failed_test_explanation": "string — If failed, trace the logic of exactly what happened on the failing test case and why it produced the wrong output. Be highly specific.",
  "optimized_approach": "string — A beautifully formatted master strategy. Explain the most optimal algorithm structurally. Break down the intuition, the 'why', and the fundamental insights required.",
  "optimized_time_complexity": "string — Big-O time of the optimal approach",
  "optimized_space_complexity": "string — Big-O space of the optimal approach",
  "improved_code": "string — Clean, enterprise-grade, highly optimized code in the SAME language as the submission. It must be fully working and idiomatic.",
  "tips": ["list of strings — 2 to 4 deeply insightful, advanced actionable tips. Go beyond 'think of edge cases'; provide specific algorithmic paradigms or mental models relevant to this problem."]
}

Rules:
- Return ONLY valid JSON, no markdown fences (NO ```json), no extra text.
- Do NOT truncate the improved_code field; it must be complete and runnable.
- Be profoundly insightful, educational, and strictly professional.
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
