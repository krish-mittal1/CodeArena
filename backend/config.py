from __future__ import annotations
"""
Application configuration via Pydantic Settings.
All values are loaded from environment variables or .env file.

PRODUCTION: Fail-fast on missing required configs, no hardcoded secrets.
"""

import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, field_validator
from typing import Optional, Union

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        env_ignore_empty=True,
    )

    # ── Environment ──────────────────────────────────────────
    environment: str = Field(default="development", description="Environment: development, staging, production")
    
    @field_validator("environment")
    @classmethod
    def validate_environment(cls, v):
        allowed = {"development", "staging", "production"}
        if v not in allowed:
            raise ValueError(f"environment must be one of {allowed}")
        return v

    # ── Database ──────────────────────────────────────────────
    database_url: str = Field(
        default="postgresql+asyncpg://postgres:password@localhost:5432/codearena",
        description="PostgreSQL connection URL"
    )
    
    @field_validator("database_url")
    @classmethod
    def validate_database_url(cls, v, info):
        if info.data.get("environment") == "production" and "password" in v:
            raise ValueError("Production database_url must not contain default password")
        return v

    # ── Redis ─────────────────────────────────────────────────
    redis_url: str = Field(
        default="redis://localhost:6379/0",
        description="Redis connection URL"
    )
    redis_enabled: bool = Field(default=True, description="Enable Redis (set to false for dev mode)")

    # ── JWT ───────────────────────────────────────────────────
    jwt_secret_key: str = Field(
        default="change-me-in-production",
        description="JWT secret key (MUST be changed in production)"
    )
    jwt_algorithm: str = Field(default="HS256", description="JWT algorithm")
    jwt_access_token_expire_minutes: int = Field(default=60, description="Access token expiry (minutes)")
    jwt_refresh_token_expire_minutes: int = Field(default=10080, description="Refresh token expiry (minutes)")  # 7 days
    
    @field_validator("jwt_secret_key")
    @classmethod
    def validate_jwt_secret(cls, v, info):
        if info.data.get("environment") == "production" and v == "change-me-in-production":
            raise ValueError("jwt_secret_key MUST be changed in production")
        if info.data.get("environment") == "development" and v == "change-me-in-production":
            raise ValueError("jwt_secret_key must be changed even in development for security")
        if len(v) < 32:
            raise ValueError("jwt_secret_key must be at least 32 characters (use secrets.token_urlsafe(32))")
        return v

    # ── Match ─────────────────────────────────────────────────
    # 30 minute matches in production-grade mode
    match_duration_seconds: int = Field(default=1800, description="Match duration (seconds)")  # 30 minutes
    matchmaking_poll_interval_ms: int = Field(default=500, description="Matchmaking poll interval (ms)")
    matchmaking_elo_initial_window: int = Field(default=100, description="Initial ELO matching window")
    matchmaking_elo_max_window: int = Field(default=500, description="Maximum ELO matching window")
    matchmaking_elo_expand_interval_seconds: int = Field(default=30, description="ELO window expansion interval (seconds)")
    matchmaking_elo_expand_step: int = Field(default=100, description="ELO window expansion step")
    matchmaking_bot_fallback_seconds: int = Field(default=15, description="Seconds before bot fallback in dev mode")

    # ── Sandbox ───────────────────────────────────────────────
    sandbox_memory_limit: str = Field(default="512m", description="Sandbox memory limit")
    sandbox_cpu_quota: int = Field(default=50000, description="Sandbox CPU quota (microseconds)")
    sandbox_cpu_period: int = Field(default=100000, description="Sandbox CPU period (microseconds)")
    sandbox_pids_limit: int = Field(default=256, description="Sandbox PID limit")
    sandbox_compile_timeout: int = Field(default=15, description="Compilation timeout (seconds)")
    sandbox_run_timeout_default: int = Field(default=5, description="Default run timeout (seconds)")
    sandbox_total_timeout: int = Field(default=60, description="Total sandbox timeout (seconds)")
    sandbox_max_concurrent: int = Field(
        default=8,
        description="Max concurrent Docker sandbox containers (judge + practice Run share this)",
    )
    sandbox_acquire_timeout_seconds: float = Field(
        default=30.0,
        description="Max seconds to wait for a free sandbox slot before failing",
    )

    # ── App ───────────────────────────────────────────────────
    app_name: str = Field(default="CodeArena", description="Application name")
    debug: bool = Field(default=False, description="Debug mode (auto-disabled in production)")
    
    @field_validator("debug")
    @classmethod
    def validate_debug(cls, v, info):
        if info.data.get("environment") == "production" and v:
            raise ValueError("debug MUST be False in production")
        return v

    # ── Server ────────────────────────────────────────────────
    host: str = Field(default="0.0.0.0", description="Server host")
    port: int = Field(default=8000, description="Server port")
    spectator_require_auth: bool = Field(
        default=True,
        description="Require valid JWT token for spectator WebSocket endpoint",
    )
    private_room_code_rate_limit: int = Field(
        default=10, description="Max room code requests per IP per minute"
    )

    # ── Reverse proxy / client IP ─────────────────────────────
    # Default False: ignore X-Forwarded-For and use the direct TCP peer.
    # Set True only when the app sits behind a reverse proxy that sets XFF
    # (Azure App Gateway / Front Door, nginx, Pangolin, etc.).
    trust_forwarded_headers: bool = Field(
        default=False,
        description="Honour X-Forwarded-For / forwarded client IP headers",
    )
    # Optional CIDR or IP list of trusted proxies. When non-empty, XFF is
    # honoured only if request.client.host is in this set, and the client IP
    # is the rightmost hop that is NOT in the set. When empty but
    # trust_forwarded_headers=True, the leftmost XFF hop is used (proxy must
    # strip client-supplied XFF before appending its own).
    trusted_proxies: list[str] = Field(
        default_factory=list,
        description="Trusted proxy IPs/CIDRs (comma-separated or JSON list in env)",
    )

    @field_validator("trusted_proxies", mode="before")
    @classmethod
    def parse_trusted_proxies(cls, v: Union[str, list, None]):
        if v is None or v == "":
            return []
        if isinstance(v, list):
            return [str(item).strip() for item in v if str(item).strip()]
        if isinstance(v, str):
            s = v.strip()
            if s.startswith("["):
                import json
                try:
                    parsed = json.loads(s)
                    if isinstance(parsed, list):
                        return [str(item).strip() for item in parsed if str(item).strip()]
                except json.JSONDecodeError:
                    pass
            return [part.strip() for part in s.split(",") if part.strip()]
        return v

    # ── Email & Frontend ──────────────────────────────────────
    frontend_url: str = Field(default="http://localhost:5173", description="Frontend base URL for links")
    smtp_host: Optional[str] = Field(default=None, description="SMTP Server Host (e.g., smtp.gmail.com)")
    smtp_port: int = Field(default=587, description="SMTP Server Port (e.g., 587)")
    smtp_user: Optional[str] = Field(default=None, description="SMTP Username")
    smtp_password: Optional[str] = Field(default=None, description="SMTP Password")
    smtp_from_email: Optional[str] = Field(default="noreply@codearena.com", description="Sender email address")

    # ── OTP / Resend ─────────────────────────────────────────
    resend_api_key: Optional[str] = Field(default=None, description="Resend API key for sending OTP emails")
    otp_from_email: str = Field(default="CodeArena <onboarding@resend.dev>", description="OTP sender email address")
    otp_expire_seconds: int = Field(default=300, description="OTP validity period (seconds)")
    otp_max_attempts: int = Field(default=5, description="Max wrong OTP attempts before lockout")
    otp_rate_limit_email: int = Field(default=3, description="Max OTP requests per email per hour")
    otp_rate_limit_ip: int = Field(default=5, description="Max OTP requests per IP per hour")

    # ── AI Providers ──────────────────────────────────────────
    gemini_api_key: Optional[str] = Field(default=None, description="Google Gemini API key")
    groq_api_key: Optional[str] = Field(default=None, description="Groq API key (preferred if both are set)")
    gemini_model: str = Field(default="gemini-2.5-flash", description="Gemini model id for AI features")

    @field_validator("gemini_api_key", "groq_api_key")
    @classmethod
    def sanitize_api_keys(cls, v: Optional[str]) -> Optional[str]:
        if v:
            return v.strip()
        return v

    @property
    def llm_api_key(self) -> Optional[str]:
        """Active LLM key — Groq takes priority over Gemini."""
        return self.groq_api_key or self.gemini_api_key

    @property
    def is_production(self) -> bool:
        return self.environment == "production"
    
    @property
    def is_development(self) -> bool:
        return self.environment == "development"


# Initialize settings and validate
try:
    settings = Settings()
except Exception as e:
    import sys
    print(f"FATAL: Configuration error: {e}", file=sys.stderr)
    sys.exit(1)
