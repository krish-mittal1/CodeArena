"""
AI Code Analysis Service — uses Groq REST API (via httpx) to analyze submitted code.
Zero external SDK dependencies required.
"""

import json
import logging
import httpx
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

GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"

# In-memory cache to prevent redundant AI calls for the same submission ID
AI_CACHE = {}


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
) -> dict:
    """
    Call Groq REST API (Llama 3) to analyze submitted code.
    Uses httpx directly — no groq SDK needed.
    """
    # 1. Check Cache first
    if submission_id and submission_id in AI_CACHE:
        logger.info(f"Returning cached AI analysis for submission {submission_id}")
        return AI_CACHE[submission_id]

    if not settings.groq_api_key:
        logger.warning("GROQ_API_KEY not set — returning placeholder analysis")
        return _fallback_analysis(verdict_status, "Groq API Key missing. Add GROQ_API_KEY to .env")

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

Analyze the code and return EXACTLY the JSON object as instructed."""

    headers = {
        "Authorization": f"Bearer {settings.groq_api_key}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {"role": "system", "content": _SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
        "response_format": {"type": "json_object"},
        "max_completion_tokens": 4096,
    }

    # Retry logic
    max_retries = 3
    last_error = ""

    for attempt in range(max_retries):
        try:
            logger.info(f"Calling Groq REST API for '{problem_title}' (Attempt {attempt + 1}/{max_retries})...")

            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(GROQ_API_URL, headers=headers, json=payload)

            if response.status_code == 429:
                last_error = "Rate limit exceeded"
                logger.warning(f"Groq 429 hit. Retrying in {(attempt + 1) * 2}s...")
                import asyncio
                await asyncio.sleep((attempt + 1) * 2)
                continue

            if response.status_code == 401:
                logger.error("Groq API key is invalid (401)")
                return _fallback_analysis(verdict_status, "Invalid Groq API Key in .env")

            if response.status_code != 200:
                last_error = f"HTTP {response.status_code}: {response.text[:100]}"
                logger.error(f"Groq API error: {last_error}")
                raise Exception(last_error)

            data = response.json()
            raw = data["choices"][0]["message"]["content"].strip()
            result = json.loads(raw)

            # Save to cache on success
            if submission_id:
                AI_CACHE[submission_id] = result

            logger.info(f"AI analysis complete for '{problem_title}'")
            return result

        except json.JSONDecodeError as e:
            logger.error(f"Groq returned invalid JSON: {e}")
            return _fallback_analysis(verdict_status, "Invalid AI response format")
        except Exception as e:
            last_error = str(e)
            logger.error(f"Groq API error (attempt {attempt + 1}): {last_error}")
            if attempt < max_retries - 1:
                import asyncio
                await asyncio.sleep((attempt + 1) * 2)
                continue

    # All retries failed
    logger.error(f"All {max_retries} Groq API attempts failed: {last_error}")
    return _fallback_analysis(verdict_status, f"AI Error: {last_error[:60]}")


def _fallback_analysis(verdict_status: str, error_reason: str = "AI analysis is currently unavailable") -> dict:
    """Return a minimal analysis object when AI is unavailable."""
    return {
        "verdict_explanation": f"Your submission received verdict: {verdict_status}.",
        "time_complexity": "N/A",
        "space_complexity": "N/A",
        "issues": [],
        "failed_test_explanation": "",
        "optimized_approach": f"{error_reason}. Please check your server configuration and API key.",
        "optimized_time_complexity": "N/A",
        "optimized_space_complexity": "N/A",
        "improved_code": "",
        "tips": ["Try to think about edge cases.", "Consider the time complexity.", "Review your algorithm."],
    }
