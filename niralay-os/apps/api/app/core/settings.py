"""
Application settings for NiralayOS.

Uses Pydantic v2 BaseSettings with full validation.
All values are sourced from environment variables or the .env file.
"""

from functools import lru_cache
from pathlib import Path

from pydantic import Field, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from app.core.environment import Environment

# Project root (apps/api/)
_API_ROOT = Path(__file__).resolve().parents[3]


class Settings(BaseSettings):
    """
    Central configuration object.

    All attributes map 1-to-1 to environment variables (case-insensitive).
    """

    model_config = SettingsConfigDict(
        env_file=_API_ROOT / ".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ------------------------------------------------------------------
    # Application
    # ------------------------------------------------------------------
    APP_NAME: str = "NiralayOS"
    APP_VERSION: str = "1.0.0"
    APP_DESCRIPTION: str = "Hospitality ERP Platform"
    API_PREFIX: str = "/api/v1"
    DEBUG: bool = False
    ENVIRONMENT: Environment = Environment.DEVELOPMENT

    # ------------------------------------------------------------------
    # Server
    # ------------------------------------------------------------------
    SERVER_HOST: str = "0.0.0.0"
    SERVER_PORT: int = Field(default=8000, ge=1, le=65535)

    # ------------------------------------------------------------------
    # CORS
    # ------------------------------------------------------------------
    ALLOWED_ORIGINS: list[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ]
    ALLOW_CREDENTIALS: bool = True
    ALLOWED_METHODS: list[str] = ["*"]
    ALLOWED_HEADERS: list[str] = ["*"]

    # ------------------------------------------------------------------
    # Database
    # ------------------------------------------------------------------
    DATABASE_HOST: str = "localhost"
    DATABASE_PORT: int = Field(default=5432, ge=1, le=65535)
    DATABASE_NAME: str = "niralayos"
    DATABASE_USER: str = "postgres"
    DATABASE_PASSWORD: str = "password"
    DATABASE_URL: str = ""

    # Connection pool
    DATABASE_POOL_SIZE: int = Field(default=10, ge=1, le=100)
    DATABASE_MAX_OVERFLOW: int = Field(default=20, ge=0, le=100)
    DATABASE_POOL_TIMEOUT: int = Field(default=30, ge=5)
    DATABASE_POOL_RECYCLE: int = Field(default=1800, ge=60)  # 30 min
    DATABASE_ECHO: bool = False  # Set True only for DB debugging

    @model_validator(mode="after")
    def _build_database_url(self) -> "Settings":
        """Construct DATABASE_URL from parts if not explicitly provided."""
        if not self.DATABASE_URL:
            self.DATABASE_URL = (
                f"postgresql://{self.DATABASE_USER}:{self.DATABASE_PASSWORD}"
                f"@{self.DATABASE_HOST}:{self.DATABASE_PORT}/{self.DATABASE_NAME}"
            )
        return self

    # ------------------------------------------------------------------
    # JWT / Security
    # ------------------------------------------------------------------
    SECRET_KEY: str = Field(
        default="CHANGE_ME_IN_PRODUCTION_use_openssl_rand_hex_32",
        min_length=32,
    )
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30, ge=1)
    REFRESH_TOKEN_EXPIRE_DAYS: int = Field(default=7, ge=1, le=90)

    # ------------------------------------------------------------------
    # Logging
    # ------------------------------------------------------------------
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"  # "json" | "text"
    LOG_FILE_PATH: str = ""   # Empty = stdout only

    # ------------------------------------------------------------------
    # Uploads
    # ------------------------------------------------------------------
    UPLOAD_PATH: str = "uploads"
    MAX_UPLOAD_SIZE_MB: int = Field(default=10, ge=1, le=100)

    # ------------------------------------------------------------------
    # Email (SMTP)
    # ------------------------------------------------------------------
    SMTP_HOST: str = ""
    SMTP_PORT: int = Field(default=587, ge=1, le=65535)
    SMTP_USERNAME: str = ""
    SMTP_PASSWORD: str = ""
    SMTP_USE_TLS: bool = True
    EMAILS_FROM_NAME: str = "NiralayOS"
    EMAILS_FROM_ADDRESS: str = "noreply@niralayos.com"

    # ------------------------------------------------------------------
    # Redis (optional — for caching / task queue)
    # ------------------------------------------------------------------
    REDIS_URL: str = ""

    # ------------------------------------------------------------------
    # Property helpers
    # ------------------------------------------------------------------
    @property
    def is_production(self) -> bool:
        return self.ENVIRONMENT.is_production

    @property
    def is_development(self) -> bool:
        return self.ENVIRONMENT.is_development

    @property
    def is_testing(self) -> bool:
        return self.ENVIRONMENT.is_testing

    @field_validator("LOG_LEVEL")
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        valid = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
        upper = v.upper()
        if upper not in valid:
            raise ValueError(f"LOG_LEVEL must be one of {valid}")
        return upper

    @field_validator("LOG_FORMAT")
    @classmethod
    def validate_log_format(cls, v: str) -> str:
        if v not in ("json", "text"):
            raise ValueError("LOG_FORMAT must be 'json' or 'text'")
        return v

    @field_validator("SECRET_KEY")
    @classmethod
    def validate_secret_key_in_production(cls, v: str) -> str:
        # We cannot check ENVIRONMENT here since validators run before
        # model_validator; this is a basic entropy check.
        if v == "CHANGE_ME_IN_PRODUCTION_use_openssl_rand_hex_32":
            import os
            env = os.getenv("ENVIRONMENT", "development").lower()
            if env == "production":
                raise ValueError(
                    "SECRET_KEY must be changed before running in production. "
                    "Generate one with: openssl rand -hex 32"
                )
        return v


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """
    Return the application settings singleton.

    Cached so environment variables are read only once per process.
    Use ``get_settings.cache_clear()`` in tests to reload settings.
    """
    return Settings()


# Module-level convenience alias
settings: Settings = get_settings()
