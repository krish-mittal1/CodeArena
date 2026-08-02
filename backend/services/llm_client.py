"""Unified LLM client — Groq (OpenAI-compatible) or Google Gemini."""

from __future__ import annotations

import json
import logging
import re
from typing import Any, Optional

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


def parse_llm_json(raw: str) -> dict[str, Any]:
    """Parse JSON from LLM output, tolerating markdown fences and extra text."""
    text = (raw or "").strip()
    if not text:
        raise json.JSONDecodeError("empty response", text, 0)

    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text, flags=re.IGNORECASE)
        text = re.sub(r"\s*```$", "", text).strip()

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        start = text.find("{")
        end = text.rfind("}")
        if start >= 0 and end > start:
            return json.loads(text[start : end + 1])
        raise


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
        return await _call_gemini(system, user, max_tokens, json_mode=True)
    raise RuntimeError("No LLM API key configured (set GROQ_API_KEY or GEMINI_API_KEY)")


async def call_text_llm(
    *,
    system: str,
    user: str,
    max_tokens: int = 512,
) -> str:
    provider = llm_provider()
    if provider == "groq":
        return await _call_groq_text(system, user, max_tokens)
    if provider == "gemini":
        return await _call_gemini(system, user, max_tokens, json_mode=False)
    raise RuntimeError("No LLM API key configured (set GROQ_API_KEY or GEMINI_API_KEY)")


# ── Singleton HTTP client ─────────────────────────────────────────────────────
# A shared httpx.AsyncClient enables connection pooling and TLS session reuse
# across all LLM calls, saving ~50-200 ms per request compared to creating a
# new client for every call.  The client is lazily initialised on first use and
# closed by close_llm_client() in the FastAPI lifespan shutdown handler.

_http_client: Optional[httpx.AsyncClient] = None


def _get_http_client() -> httpx.AsyncClient:
    """Return the shared HTTP client, creating it on first call."""
    global _http_client
    if _http_client is None or _http_client.is_closed:
        _http_client = httpx.AsyncClient(
            timeout=httpx.Timeout(connect=10.0, read=90.0, write=10.0, pool=5.0),
            limits=httpx.Limits(max_connections=20, max_keepalive_connections=10),
        )
    return _http_client


async def close_llm_client() -> None:
    """Close the shared HTTP client. Call this from lifespan shutdown."""
    global _http_client
    if _http_client is not None and not _http_client.is_closed:
        await _http_client.aclose()
        _http_client = None


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
    client = _get_http_client()
    response = await client.post(GROQ_API_URL, headers=headers, json=payload)
    if response.status_code != 200:
        raise RuntimeError(f"Groq HTTP {response.status_code}: {response.text[:200]}")
    return response.json()["choices"][0]["message"]["content"].strip()


async def _call_groq_text(system: str, user: str, max_tokens: int) -> str:
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
        "max_completion_tokens": max_tokens,
    }
    client = _get_http_client()
    response = await client.post(GROQ_API_URL, headers=headers, json=payload)
    if response.status_code != 200:
        raise RuntimeError(f"Groq HTTP {response.status_code}: {response.text[:200]}")
    return response.json()["choices"][0]["message"]["content"].strip()


async def _call_gemini(system: str, user: str, max_tokens: int, *, json_mode: bool) -> str:
    model = _gemini_model()
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
    params = {"key": settings.gemini_api_key}
    payload = {
        "systemInstruction": {"parts": [{"text": system}]},
        "contents": [{"parts": [{"text": user}]}],
        "generationConfig": {
            "maxOutputTokens": max_tokens,
        },
    }
    if json_mode:
        payload["generationConfig"]["responseMimeType"] = "application/json"
    client = _get_http_client()
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
