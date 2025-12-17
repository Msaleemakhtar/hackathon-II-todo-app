from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application configuration loaded from environment variables."""

    # Database
    database_url: str
    test_database_url: str | None = None

    # Database Connection Pool Settings
    db_pool_min: int = 5
    db_pool_max: int = 10

    # Gemini AI
    gemini_api_key: str

    # Better Auth
    better_auth_secret: str
    better_auth_url: str = "http://localhost:3000"

    # CORS
    cors_origins: list[str] = ["http://localhost:3000"]

    # JWT Cache Configuration
    jwt_cache_size: int = 1000
    jwt_cache_ttl: int = 300  # seconds

    # Application Settings
    debug: bool = False
    log_level: str = "INFO"
    environment: str = "development"

    # Server Configuration
    host: str = "0.0.0.0"
    port: int = 8000

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
