"""AI hint prompts — pre-submit nudge, pattern, outline."""

from __future__ import annotations

import logging
from typing import Optional

from backend.services.llm_client import call_text_llm, llm_provider, parse_llm_json

logger = logging.getLogger(__name__)

_MAX_DESC_CHARS = 2500

_HINT_PROMPTS = {
    "nudge": "Give ONE short nudge (2-3 sentences). Do NOT name the full algorithm or give code. Point at what to notice in the problem.",
    "pattern": "Name the likely algorithm pattern (e.g. sliding window, two pointers) and explain in 3-4 sentences WHEN to use it on this problem. No code.",
    "outline": "Give 4-6 numbered pseudocode steps for the optimal approach. No actual code in any language.",
}


def _clip(text: Optional[str], limit: int = _MAX_DESC_CHARS) -> str:
    if not text:
        return ""
    text = str(text).strip()
    return text if len(text) <= limit else text[:limit] + "…"


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
            "ok": False,
        }

    system = (
        f"You are a coding interview tutor. {_HINT_PROMPTS[hint_level]} "
        "Reply with plain text only — no JSON, no markdown fences, no code blocks."
    )

    prompt = f"""Problem: {problem_title}

{_clip(problem_description)}

Constraints: {_clip(constraints, 500) or 'Not specified'}"""

    last_error = ""
    for attempt in range(3):
        try:
            raw = await call_text_llm(system=system, user=prompt, max_tokens=512)
            content = raw.strip()
            if content.startswith("{"):
                try:
                    parsed = parse_llm_json(content)
                    content = str(parsed.get("content") or parsed.get("hint") or content).strip()
                except Exception:
                    pass
            if content:
                return {"hint_level": hint_level, "content": content, "ok": True}
            last_error = "empty response"
        except Exception as exc:
            last_error = str(exc)
            logger.warning("Hint generation failed (attempt %d): %s", attempt + 1, exc)

    msg = last_error
    if "401" in msg or "403" in msg or "API key" in msg.lower():
        content = "AI hints unavailable — check GEMINI_API_KEY on the server."
    elif "400" in msg:
        content = "AI hints unavailable — Gemini model or API config issue. Check server logs."
    else:
        content = "Could not generate hint right now. Try again in a few seconds."
    return {"hint_level": hint_level, "content": content, "ok": False}
