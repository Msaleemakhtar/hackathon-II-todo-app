from typing import Literal

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings with validation."""

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", case_sensitive=False, extra="ignore"
    )

    # Application
    APP_NAME: str = "Todo App API"
    ENVIRONMENT: Literal["development", "testing", "production"] = "development"
    DEBUG: bool = False

    # Database
    DATABASE_URL: str = Field(..., description="Main database connection string")
    TEST_DATABASE_URL: str | None = Field(
        None, description="Test database connection string (overrides main for testing)"
    )

    # Database pooling settings (primarily for PostgreSQL)
    # Optimized for medium-scale concurrent usage (10-100 users)
    DB_POOL_MIN: int = 5  # Increased from 2 for better responsiveness
    DB_POOL_MAX: int = 10  # Increased from 5 for higher concurrency
    DB_POOL_RECYCLE: int = 3600
    DB_CONNECTION_TIMEOUT: int = 30

    # Better Auth
    BETTER_AUTH_SECRET: str = Field(
        ..., min_length=32, description="Better Auth secret (32+ chars)"
    )

    @field_validator("BETTER_AUTH_SECRET")
    @classmethod
    def validate_better_auth_secret(cls, v: str) -> str:
        """Validate that the Better Auth secret key is at least 32 characters long."""
        if len(v) < 32:
            raise ValueError("BETTER_AUTH_SECRET must be at least 32 characters")
        return v

    # CORS
    CORS_ORIGINS: list[str] = Field(
        default=[
            "http://localhost:3000",
            "http://localhost:5173",
            "http://localhost:8080",
            "http://localhost:8000",
        ],
        description="Allowed CORS origins",
    )

    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000


settings = Settings()


# Startup validation
def validate_settings():
    """Validate settings on application startup."""
    assert len(settings.BETTER_AUTH_SECRET) >= 32, "Better Auth secret too short"
    print(f"✅ Settings validated: {settings.APP_NAME}")
