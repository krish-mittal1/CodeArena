"""AI hint prompts — pre-submit nudge, pattern, outline."""

from __future__ import annotations

import json
import logging
from typing import Optional

from backend.config import settings
from backend.services.llm_client import call_json_llm, llm_provider

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

    if not llm_provider():
        return {
            "hint_level": hint_level,
            "content": "AI hints are unavailable. Set GROQ_API_KEY or GEMINI_API_KEY in server config.",
        }

    system = f"You are a coding interview tutor. {_HINT_PROMPTS[hint_level]} Return JSON: {{\"content\": \"...\"}}"

    prompt = f"""Problem: {problem_title}

{problem_description}

Constraints: {constraints or 'Not specified'}"""

    try:
        raw = await call_json_llm(system=system, user=prompt, max_tokens=512)
        data = json.loads(raw)
        return {"hint_level": hint_level, "content": data.get("content", "")}
    except Exception as exc:
        logger.warning("Hint generation failed: %s", exc)
        msg = str(exc)
        if "401" in msg or "403" in msg or "API key" in msg.lower():
            content = "AI hints unavailable — check GEMINI_API_KEY on the server."
        elif "400" in msg:
            content = "AI hints unavailable — Gemini model or API config issue. Check server logs."
        else:
            content = "Could not generate hint right now. Try again in a few seconds."
        return {"hint_level": hint_level, "content": content}
