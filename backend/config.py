"""
config.py — Centralised configuration loader.

Reads all required and optional environment variables from the .env file
using python-dotenv. Import `settings` anywhere in the app to access config.
"""

import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Settings:
    # ── Database ─────────────────────────────────────────────────────────────
    database_url: str

    # ── Auth ─────────────────────────────────────────────────────────────────
    secret_key: str
    algorithm: str
    access_token_expire_minutes: int

    # ── External APIs ────────────────────────────────────────────────────────
    # data.gov.in — required for AGMARKNET mandi prices
    datagov_api_key: str

    # ── Email (Resend) ────────────────────────────────────────────────────────
    resend_api_key: str

    # ── App ──────────────────────────────────────────────────────────────────
    debug: bool
    app_env: str   # "development" | "staging" | "production"


def _require(key: str) -> str:
    """Return the env var value, raising an error if it is not set."""
    value = os.getenv(key)
    if not value:
        raise RuntimeError(
            f"Required environment variable '{key}' is not set. "
            f"Copy .env.example to .env and fill in the value."
        )
    return value


def _optional(key: str, default: str = "") -> str:
    return os.getenv(key, default)


# Singleton settings object — imported across the app
settings = Settings(
    database_url=_require("DATABASE_URL"),
    secret_key=_require("SECRET_KEY"),
    algorithm=_optional("ALGORITHM", "HS256"),
    access_token_expire_minutes=int(_optional("ACCESS_TOKEN_EXPIRE_MINUTES", "60")),
    datagov_api_key=_optional("DATAGOV_API_KEY"),   # Optional — only needed for mandi endpoint
    resend_api_key=_optional("RESEND_API_KEY"),
    debug=_optional("DEBUG", "false").lower() == "true",
    app_env=_optional("APP_ENV", "development"),
)
