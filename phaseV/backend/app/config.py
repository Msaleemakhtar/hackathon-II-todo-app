import json

from pydantic import field_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application configuration loaded from environment variables."""

    # Database
    database_url: str
    test_database_url: str | None = None

    # Database Connection Pool Settings
    db_pool_min: int = 5
    db_pool_max: int = 10

    # AI API Keys
    openai_api_key: str | None = None
    gemini_api_key: str | None = None

    # Better Auth (optional - not used in Phase III)
    better_auth_secret: str | None = None
    better_auth_url: str = "http://localhost:3000"

    # CORS
    cors_origins: list[str] | str = ["http://localhost:3000"]

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, v):
        """Parse CORS origins from JSON string or return as-is if already a list."""
        if isinstance(v, str):
            try:
                return json.loads(v)
            except json.JSONDecodeError:
                # If not JSON, treat as comma-separated
                return [origin.strip() for origin in v.split(",")]
        return v

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

    # MCP Server Configuration
    mcp_server_url: str = "http://localhost:8001/mcp"

    # SMTP Email Configuration
    smtp_host: str = "smtp.gmail.com"
    smtp_port: int = 587
    smtp_username: str | None = None
    smtp_password: str | None = None
    smtp_from_email: str | None = None
    smtp_from_name: str = "Todo App Reminders"

    # Email Delivery Service Configuration
    email_delivery_group_id: str = "email-delivery-consumer-group"

    # Dapr Configuration
    use_dapr: bool = False

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
