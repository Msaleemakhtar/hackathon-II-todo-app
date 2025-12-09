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
    DB_POOL_MIN: int = 2
    DB_POOL_MAX: int = 5
    DB_POOL_RECYCLE: int = 3600
    DB_CONNECTION_TIMEOUT: int = 30

    # JWT
    JWT_SECRET_KEY: str = Field(
        ..., min_length=64, description="JWT secret (64+ hex chars)"
    )

    @field_validator("JWT_SECRET_KEY")
    @classmethod
    def validate_jwt_secret(cls, v: str) -> str:
        """Validate that the JWT secret key is at least 64 characters long."""
        if len(v) < 64:
            raise ValueError("JWT_SECRET_KEY must be at least 64 characters (256 bits)")
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
    assert len(settings.JWT_SECRET_KEY) >= 64, "JWT secret too short"
    print(f"✅ Settings validated: {settings.APP_NAME}")
