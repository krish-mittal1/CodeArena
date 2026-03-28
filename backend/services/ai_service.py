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


# In-memory cache to prevent redundant AI calls for the same submission ID
# Keys are submission IDs (str), values are the analysis dicts
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
    submission_id: Optional[str] = None,  # Added for caching
) -> dict:
    """
    Call Gemini to analyze the user's submitted code.
    Returns a structured dict with analysis or a fallback on failure.
    """
    # 1. Check Cache first
    if submission_id and submission_id in AI_CACHE:
        logger.info(f"Returning cached AI analysis for submission {submission_id}")
        return AI_CACHE[submission_id]

    if not settings.gemini_api_key:
        logger.warning("GEMINI_API_KEY not set — returning placeholder analysis")
        return _fallback_analysis(verdict_status)

    try:
        import google.generativeai as genai
        genai.configure(api_key=settings.gemini_api_key)
        
        # Use a Lite model for much higher quota / better RPM for free tier
        model = genai.GenerativeModel(
            model_name="gemini-2.0-flash-lite",
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

        # Retry logic for 429 Errors
        max_retries = 3
        last_error = ""
        for attempt in range(max_retries):
            try:
                logger.info(f"Calling Gemini for {problem_title} (Attempt {attempt+1})...")
                response = model.generate_content(prompt)
                raw = response.text.strip()
                break
            except Exception as e:
                last_error = str(e)
                if "429" in last_error or "quota" in last_error.lower():
                    logger.warning(f"Gemini 429 hit. Waiting... {last_error}")
                    if attempt < max_retries - 1:
                        wait_time = (attempt + 1) * 3
                        import asyncio
                        await asyncio.sleep(wait_time)
                        continue
                raise e
        else:
             raise Exception(f"Failed after {max_retries} retries: {last_error}")

        # Strip any accidental markdown fences
        if raw.startswith("```"):
            raw = raw.split("\n", 1)[1]
            if raw.endswith("```"):
                raw = raw.rsplit("```", 1)[0]

        result = json.loads(raw)
        
        # 2. Save to Cache on success
        if submission_id:
            AI_CACHE[submission_id] = result
            
        return result

    except json.JSONDecodeError as e:
        logger.error(f"Gemini returned invalid JSON: {e}")
        return _fallback_analysis(verdict_status, "Invalid AI response format")
    except Exception as e:
        error_msg = str(e)
        logger.error(f"Gemini API error: {error_msg}")
        # Detect quota and key issues specifically
        if "API_KEY_INVALID" in error_msg or "400" in error_msg:
            return _fallback_analysis(verdict_status, "Invalid Gemini API Key in .env")
        if "429" in error_msg or "quota" in error_msg.lower():
            return _fallback_analysis(verdict_status, "AI Quota Exceeded (Free Tier limit). Please wait 1 minute and try again.")
        return _fallback_analysis(verdict_status, f"AI Error: {error_msg[:50]}...")


def _fallback_analysis(verdict_status: str, error_reason: str = "AI analysis is currently unavailable") -> dict:
    """Return a minimal analysis object when Gemini is unavailable."""
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
