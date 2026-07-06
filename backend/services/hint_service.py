"""AI hint prompts — pre-submit nudge, pattern, outline."""

from __future__ import annotations

import json
import logging
from typing import Optional

import httpx

from backend.config import settings
from backend.services.ai_service import GROQ_API_URL, _fallback_analysis

logger = logging.getLogger(__name__)

_HINT_PROMPTS = {
    "nudge": "Give ONE short nudge (2-3 sentences). Do NOT name the full algorithm or give code. Point at what to notice in the problem.",
    "pattern": "Name the likely algorithm pattern (e.g. sliding window, two pointers) and explain in 3-4 sentences WHEN to use it on this problem. No code.",
    "outline": "Give 4-6 numbered pseudocode steps for the optimal approach. No actual code in any language.",
}


async def get_hint(
    *,
    hint_level: str,
    problem_title: str,
    problem_description: str,
    constraints: Optional[str],
) -> dict:
    if hint_level not in _HINT_PROMPTS:
        hint_level = "nudge"

    if not settings.groq_api_key:
        return {"hint_level": hint_level, "content": "AI hints are unavailable. Check GROQ_API_KEY in server config."}

    system = f"You are a coding interview tutor. {_HINT_PROMPTS[hint_level]} Return JSON: {{\"content\": \"...\"}}"

    prompt = f"""Problem: {problem_title}

{problem_description}

Constraints: {constraints or 'Not specified'}"""

    headers = {"Authorization": f"Bearer {settings.groq_api_key}", "Content-Type": "application/json"}
    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": prompt},
        ],
        "response_format": {"type": "json_object"},
        "max_completion_tokens": 512,
    }

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(GROQ_API_URL, headers=headers, json=payload)
        if response.status_code != 200:
            raise RuntimeError(f"HTTP {response.status_code}")
        raw = response.json()["choices"][0]["message"]["content"]
        data = json.loads(raw)
        return {"hint_level": hint_level, "content": data.get("content", "")}
    except Exception as exc:
        logger.warning("Hint generation failed: %s", exc)
        return {"hint_level": hint_level, "content": "Could not generate hint right now. Try breaking the problem into smaller cases."}
