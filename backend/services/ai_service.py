"""
AI Code Analysis Service - uses Groq REST API (via httpx) to analyze submitted code.
Zero external SDK dependencies required.
"""

import json
import logging
from typing import Optional

import httpx

from backend.config import settings

logger = logging.getLogger(__name__)

_SYSTEM_PROMPT = """You are an expert competitive programming mentor and a patient teacher.
Your job is to explain the user's code in a way that is easy to understand for someone practicing interview problems.
Sound clear, warm, and direct. Prefer simple words over fancy words.
Teach like a strong mentor, not like a research paper.

Analyze the submitted code and return a JSON object with EXACTLY these keys:

{
  "problem_concept": "string - 2 to 4 short paragraphs. Explain the core concept of the problem, what the problem is really asking, and what pattern or data structure is usually used.",
  "verdict_explanation": "string - 2 to 4 short paragraphs. Explain why the code passed or failed in plain language. Mention the key idea, important edge cases, and the main reason behind the verdict.",
  "submitted_approach": "string - Explain the user's current approach in simple language. Mention the pattern if recognizable.",
  "time_complexity": "string - Big-O time complexity of submitted code, e.g. O(N log N)",
  "space_complexity": "string - Big-O space complexity of submitted code, e.g. O(N)",
  "worst_approach": "string - Explain a slower but still reasonable brute-force or weaker approach. Mention when someone might think of it first.",
  "worst_time_complexity": "string - Big-O time of the slower or brute-force approach",
  "worst_space_complexity": "string - Big-O space of the slower or brute-force approach",
  "issues": ["list of strings - each item should be one specific issue in plain language. Keep each item short and concrete. Empty list [] if code is correct and clean"],
  "failed_test_explanation": "string - If the code failed, explain the failing test case step by step in simple language. If the code passed, return an empty string.",
  "optimized_approach": "string - Explain the best approach like a mini editorial. Use short paragraphs or short numbered steps. Cover: the idea, how it works, why it is correct, and what to watch out for.",
  "optimized_time_complexity": "string - Big-O time of the optimal approach",
  "optimized_space_complexity": "string - Big-O space of the optimal approach",
  "alternative_approaches": [
    {
      "name": "string - short label for the approach",
      "summary": "string - 1 to 3 short paragraphs on how the approach works",
      "time_complexity": "string - Big-O time complexity",
      "space_complexity": "string - Big-O space complexity",
      "when_to_use": "string - when this approach is useful or why someone may choose it"
    }
  ],
  "improved_code": "string - Clean, correct, idiomatic code in the SAME language as the submission. It must be fully working and easy to read.",
  "tips": ["list of strings - 2 to 4 short, practical takeaways. Each tip should be something the user can remember for similar problems."]
}

Rules:
- Return ONLY valid JSON, no markdown fences (NO ```json), no extra text.
- Do NOT truncate the improved_code field; it must be complete and runnable.
- Keep explanations easy to scan.
- Avoid buzzwords like "architectural", "enterprise-grade", "profoundly insightful", or "master strategy".
- Do not sound robotic.
- If the code is accepted, still explain why it works and what pattern it is using.
- If the problem uses a classic pattern like sliding window, two pointers, binary search, prefix sum, linked list reversal, etc., name the pattern clearly.
- Always fill in the worst_approach and optimized_approach fields.
- If there are other realistic approaches, include 1 to 3 items in alternative_approaches. If there are no meaningful alternatives, return [].
- Make the analysis teach the user the whole problem, not only the submitted code.
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
    Uses httpx directly - no Groq SDK needed.
    """
    if submission_id and submission_id in AI_CACHE:
        logger.info("Returning cached AI analysis for submission %s", submission_id)
        return AI_CACHE[submission_id]

    if not settings.groq_api_key:
        logger.warning("GROQ_API_KEY not set - returning placeholder analysis")
        return _fallback_analysis(verdict_status, "Groq API key missing. Add GROQ_API_KEY to .env")

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

Before answering, think about what would help a learner understand this problem quickly.
Keep the explanation simple, specific, and helpful.
Return EXACTLY the JSON object as instructed."""

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

    max_retries = 3
    last_error = ""

    for attempt in range(max_retries):
        try:
            logger.info("Calling Groq REST API for '%s' (Attempt %d/%d)...", problem_title, attempt + 1, max_retries)

            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(GROQ_API_URL, headers=headers, json=payload)

            if response.status_code == 429:
                last_error = "Rate limit exceeded"
                logger.warning("Groq 429 hit. Retrying in %ss...", (attempt + 1) * 2)
                import asyncio
                await asyncio.sleep((attempt + 1) * 2)
                continue

            if response.status_code == 401:
                logger.error("Groq API key is invalid (401)")
                return _fallback_analysis(verdict_status, "Invalid Groq API key in .env")

            if response.status_code != 200:
                last_error = f"HTTP {response.status_code}: {response.text[:100]}"
                logger.error("Groq API error: %s", last_error)
                raise Exception(last_error)

            data = response.json()
            raw = data["choices"][0]["message"]["content"].strip()
            result = json.loads(raw)

            if submission_id:
                AI_CACHE[submission_id] = result

            logger.info("AI analysis complete for '%s'", problem_title)
            return result

        except json.JSONDecodeError as e:
            logger.error("Groq returned invalid JSON: %s", e)
            return _fallback_analysis(verdict_status, "Invalid AI response format")
        except Exception as e:
            last_error = str(e)
            logger.error("Groq API error (attempt %d): %s", attempt + 1, last_error)
            if attempt < max_retries - 1:
                import asyncio
                await asyncio.sleep((attempt + 1) * 2)
                continue

    logger.error("All %d Groq API attempts failed: %s", max_retries, last_error)
    return _fallback_analysis(verdict_status, f"AI Error: {last_error[:60]}")


def _fallback_analysis(verdict_status: str, error_reason: str = "AI analysis is currently unavailable") -> dict:
    """Return a minimal analysis object when AI is unavailable."""
    return {
        "problem_concept": "This problem still has a core pattern behind it, but the AI explanation is not available right now. Try identifying the main data structure, the key state you need to track, and the simplest brute-force version first.",
        "verdict_explanation": f"Your submission received verdict: {verdict_status}. A full AI explanation is not available right now.",
        "submitted_approach": "The system could not generate a reliable explanation of your exact approach right now.",
        "time_complexity": "N/A",
        "space_complexity": "N/A",
        "worst_approach": "Start from the most direct brute-force idea, then look for repeated work you can remove.",
        "worst_time_complexity": "N/A",
        "worst_space_complexity": "N/A",
        "issues": [],
        "failed_test_explanation": "",
        "optimized_approach": f"{error_reason}. Please check your server configuration and API key.",
        "optimized_time_complexity": "N/A",
        "optimized_space_complexity": "N/A",
        "alternative_approaches": [],
        "improved_code": "",
        "tips": [
            "Test small edge cases first.",
            "Check the time complexity before submitting.",
            "Compare your approach with the common pattern for this problem type.",
        ],
    }
