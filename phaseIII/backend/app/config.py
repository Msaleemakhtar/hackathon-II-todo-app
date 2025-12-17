"""Application configuration settings."""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Database configuration
    DATABASE_URL: str
    DB_POOL_MIN: int = 5
    DB_POOL_MAX: int = 10

    # Better Auth configuration
    BETTER_AUTH_SECRET: str

    # JWT cache configuration
    JWT_CACHE_SIZE: int = 1000
    JWT_CACHE_TTL: int = 300  # seconds

    # Application settings
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"

    # Server configuration
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",  # Ignore extra environment variables
    )


# Global settings instance
settings = Settings()
