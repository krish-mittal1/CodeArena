from __future__ import annotations
"""
Application configuration via Pydantic Settings.
All values are loaded from environment variables or .env file.

PRODUCTION: Fail-fast on missing required configs, no hardcoded secrets.
"""

import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, field_validator
from typing import Optional

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
        if len(v) < 32:
            raise ValueError("jwt_secret_key must be at least 32 characters")
        return v

    # ── Match ─────────────────────────────────────────────────
    # 30 minute matches in production-grade mode
    match_duration_seconds: int = Field(default=1800, description="Match duration (seconds)")  # 30 minutes
    matchmaking_poll_interval_ms: int = Field(default=500, description="Matchmaking poll interval (ms)")
    matchmaking_elo_initial_window: int = Field(default=100, description="Initial ELO matching window")
    matchmaking_elo_max_window: int = Field(default=500, description="Maximum ELO matching window")
    matchmaking_elo_expand_interval_seconds: int = Field(default=30, description="ELO window expansion interval (seconds)")
    matchmaking_elo_expand_step: int = Field(default=100, description="ELO window expansion step")

    # ── Sandbox ───────────────────────────────────────────────
    sandbox_memory_limit: str = Field(default="512m", description="Sandbox memory limit")
    sandbox_cpu_quota: int = Field(default=50000, description="Sandbox CPU quota (microseconds)")
    sandbox_cpu_period: int = Field(default=100000, description="Sandbox CPU period (microseconds)")
    sandbox_pids_limit: int = Field(default=256, description="Sandbox PID limit")
    sandbox_compile_timeout: int = Field(default=15, description="Compilation timeout (seconds)")
    sandbox_run_timeout_default: int = Field(default=5, description="Default run timeout (seconds)")
    sandbox_total_timeout: int = Field(default=60, description="Total sandbox timeout (seconds)")

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
    
    # ── Email & Frontend ──────────────────────────────────────
    frontend_url: str = Field(default="http://localhost:5173", description="Frontend base URL for links")
    smtp_host: Optional[str] = Field(default=None, description="SMTP Server Host (e.g., smtp.gmail.com)")
    smtp_port: int = Field(default=587, description="SMTP Server Port (e.g., 587)")
    smtp_user: Optional[str] = Field(default=None, description="SMTP Username")
    smtp_password: Optional[str] = Field(default=None, description="SMTP Password")
    smtp_from_email: Optional[str] = Field(default="noreply@codearena.com", description="Sender email address")

    # ── OTP / Resend ─────────────────────────────────────────
    resend_api_key: Optional[str] = Field(default=None, description="Resend API key for sending OTP emails")
    otp_from_email: str = Field(default="CodeArena <noreply@codearena.com>", description="OTP sender email address")
    otp_expire_seconds: int = Field(default=300, description="OTP validity period (seconds)")
    otp_max_attempts: int = Field(default=5, description="Max wrong OTP attempts before lockout")
    otp_rate_limit_email: int = Field(default=3, description="Max OTP requests per email per hour")
    otp_rate_limit_ip: int = Field(default=5, description="Max OTP requests per IP per hour")

    # ── AI Providers ──────────────────────────────────────────
    gemini_api_key: Optional[str] = Field(default=None, description="Google Gemini API key")
    groq_api_key: Optional[str] = Field(default=None, description="Groq API key for Llama 3 analysis")

    @field_validator("gemini_api_key", "groq_api_key")
    @classmethod
    def sanitize_api_keys(cls, v: Optional[str]) -> Optional[str]:
        if v:
            return v.strip()
        return v

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
