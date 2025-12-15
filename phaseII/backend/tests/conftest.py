"""Pytest configuration for Todo App Backend with PostgreSQL test database."""

import os
import asyncio
from typing import AsyncGenerator
import pytest
import pytest_asyncio
import httpx
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlmodel import SQLModel
from urllib.parse import urlparse, parse_qs, urlencode


def clean_database_url(original_url: str) -> str:
    """Clean database URL by removing problematic parameters for asyncpg."""
    if not original_url or 'asyncpg' not in original_url:
        return original_url

    # Parse the URL
    parsed = urlparse(original_url)

    # Parse the query parameters
    query_params = parse_qs(parsed.query)

    # Remove problematic parameters that asyncpg doesn't support
    params_to_remove = ['channel_binding', 'sslmode', 'sslcert', 'sslkey', 'sslrootcert']
    for param in params_to_remove:
        query_params.pop(param, None)

    # Rebuild the query string
    new_query = urlencode(query_params, doseq=True)

    # Reconstruct the URL without problematic parameters
    cleaned_url = parsed._replace(query=new_query).geturl()

    return cleaned_url


# Load environment variables from .env file if it exists
if os.path.exists(".env"):
    with open(".env", "r") as f:
        for line in f:
            if line.strip() and not line.startswith("#") and "=" in line:
                key, value = line.strip().split("=", 1)
                os.environ[key] = value

# Override environment variables for testing BEFORE importing settings
os.environ["ENVIRONMENT"] = "testing"

# Get the original TEST_DATABASE_URL from environment or .env file
original_test_db_url = os.getenv("TEST_DATABASE_URL", "")
if original_test_db_url:
    # Clean the URL to remove problematic parameters
    cleaned_test_db_url = clean_database_url(original_test_db_url)
    os.environ["TEST_DATABASE_URL"] = cleaned_test_db_url
else:
    # If no TEST_DATABASE_URL is provided, use a default
    # Get the main DATABASE_URL and clean it
    main_db_url = os.getenv("DATABASE_URL", "postgresql+asyncpg://neondb_owner:npg_zTkq1ABHR8uC@ep-mute-tooth-adbf0l4h-pooler.c-2.us-east-1.aws.neon.tech/neondb")
    cleaned_main_db_url = clean_database_url(main_db_url)
    os.environ["TEST_DATABASE_URL"] = cleaned_main_db_url

# Use the actual BETTER_AUTH_SECRET from environment, do not provide a default
# This ensures that tokens created in tests will match the secret used by the app
actual_auth_secret = os.getenv("BETTER_AUTH_SECRET")
if not actual_auth_secret:
    raise ValueError("BETTER_AUTH_SECRET environment variable is required for testing")

os.environ["BETTER_AUTH_SECRET"] = actual_auth_secret

# Import after environment variables are set
from src.main import app
from src.core.config import settings, validate_settings
from src.core.database import get_db, init_db

# Import all models to ensure they're registered with SQLModel.metadata
from src.models import (
    User,
    Task,
    Tag,
    Category,
    TaskTagLink,
    Reminder,
    WebVital,
    AnalyticsEvent,
    TaskOrder,
    UserSubscription,
)


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the session."""
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="session", autouse=True)
async def setup_test_database():
    """Set up the test database before tests run."""
    # Validate settings
    validate_settings()

    # Create engine with test database
    engine = create_async_engine(settings.TEST_DATABASE_URL)

    # Drop all existing tables and recreate them
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)
        await conn.run_sync(SQLModel.metadata.create_all)

    yield

    # Clean up after all tests
    # Note: We're not dropping all tables here to avoid issues with Neon's connection pooling
    # Instead, we rely on transaction rollback in each test for isolation

    await engine.dispose()


@pytest_asyncio.fixture
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """Create a database session for testing with rollback after each test."""
    engine = create_async_engine(settings.TEST_DATABASE_URL)
    async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        # Start a transaction
        await session.begin()

        try:
            yield session
        finally:
            # Rollback the transaction to maintain data isolation between tests
            if session.in_transaction():
                await session.rollback()

    await engine.dispose()


@pytest_asyncio.fixture
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """Create an HTTP client for testing with mocked database."""

    def override_get_db():
        return db_session

    app.dependency_overrides[get_db] = override_get_db

    # Create AsyncClient with the FastAPI app for testing
    # The correct way to create an async client for FastAPI testing
    client = AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://testserver")
    try:
        yield client
    finally:
        app.dependency_overrides.clear()