"""Unified LLM client — Groq (OpenAI-compatible) or Google Gemini."""

from __future__ import annotations

import logging
from typing import Optional

import httpx

from backend.config import settings

logger = logging.getLogger(__name__)

GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_MODEL = "llama-3.3-70b-versatile"


def _gemini_model() -> str:
    return settings.gemini_model or "gemini-2.5-flash"


def llm_provider() -> Optional[str]:
    if settings.groq_api_key:
        return "groq"
    if settings.gemini_api_key:
        return "gemini"
    return None


async def call_json_llm(
    *,
    system: str,
    user: str,
    max_tokens: int = 4096,
) -> str:
    provider = llm_provider()
    if provider == "groq":
        return await _call_groq(system, user, max_tokens)
    if provider == "gemini":
        return await _call_gemini(system, user, max_tokens)
    raise RuntimeError("No LLM API key configured (set GROQ_API_KEY or GEMINI_API_KEY)")


async def _call_groq(system: str, user: str, max_tokens: int) -> str:
    headers = {
        "Authorization": f"Bearer {settings.groq_api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": GROQ_MODEL,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        "response_format": {"type": "json_object"},
        "max_completion_tokens": max_tokens,
    }
    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.post(GROQ_API_URL, headers=headers, json=payload)
    if response.status_code != 200:
        raise RuntimeError(f"Groq HTTP {response.status_code}: {response.text[:200]}")
    return response.json()["choices"][0]["message"]["content"].strip()


async def _call_gemini(system: str, user: str, max_tokens: int) -> str:
    model = _gemini_model()
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
    params = {"key": settings.gemini_api_key}
    payload = {
        "systemInstruction": {"parts": [{"text": system}]},
        "contents": [{"parts": [{"text": user}]}],
        "generationConfig": {
            "responseMimeType": "application/json",
            "maxOutputTokens": max_tokens,
        },
    }
    async with httpx.AsyncClient(timeout=90.0) as client:
        response = await client.post(url, params=params, json=payload)
    if response.status_code != 200:
        raise RuntimeError(f"Gemini HTTP {response.status_code}: {response.text[:300]}")
    data = response.json()
    candidates = data.get("candidates") or []
    if not candidates:
        block = data.get("promptFeedback", {}).get("blockReason", "no candidates")
        raise RuntimeError(f"Gemini blocked response: {block}")
    parts = candidates[0].get("content", {}).get("parts") or []
    if not parts:
        raise RuntimeError("Gemini returned empty content")
    return parts[0].get("text", "").strip()
