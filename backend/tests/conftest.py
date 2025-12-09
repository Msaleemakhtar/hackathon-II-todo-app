import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.pool import NullPool
from sqlmodel import SQLModel
from unittest.mock import Mock
from unittest import mock

from src.main import app
from src.core.config import settings
from src.core.database import get_db
from src.routers import auth

# Test database URL (separate from dev database)
# If TEST_DATABASE_URL is SQLite but not available, fall back to main PostgreSQL database
# with transaction rollback for test isolation
TEST_DATABASE_URL = settings.TEST_DATABASE_URL or settings.DATABASE_URL

# If SQLite is specified but not available, use main PostgreSQL database
if "sqlite" in TEST_DATABASE_URL:
    try:
        # Try to import sqlite3 to check if it's available
        import sqlite3
    except ImportError:
        # SQLite not available, use main PostgreSQL database
        print("⚠️ SQLite not available, using main PostgreSQL database with transaction rollback for test isolation")
        TEST_DATABASE_URL = settings.DATABASE_URL


@pytest_asyncio.fixture(scope="function", autouse=True)
async def setup_test_db():
    """Create test database schema before each test."""
    engine = create_async_engine(TEST_DATABASE_URL, echo=False, poolclass=NullPool)
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)
        await conn.run_sync(SQLModel.metadata.create_all)
    await engine.dispose()
    yield


@pytest_asyncio.fixture
async def db_session():
    """Provide a clean database session per test."""
    # Create a fresh engine for this test
    engine = create_async_engine(TEST_DATABASE_URL, echo=False, poolclass=NullPool)

    # Create a connection and begin a transaction
    connection = await engine.connect()
    transaction = await connection.begin()

    # Create a session bound to this connection
    session = AsyncSession(bind=connection, expire_on_commit=False)

    try:
        yield session
    finally:
        await session.close()
        # Rollback the transaction to undo all changes made during the test
        await transaction.rollback()
        await connection.close()
        await engine.dispose()


@pytest.fixture(autouse=True)
def reset_rate_limiter():
    """Reset rate limiter storage before each test."""
    # Clear the rate limiter storage for both app and auth router limiters
    for limiter in [app.state.limiter, auth.limiter]:
        if hasattr(limiter, '_storage'):
            limiter._storage.storage.clear()
        if hasattr(limiter, 'storage'):
            if hasattr(limiter.storage, 'storage'):
                limiter.storage.storage.clear()
    yield


@pytest_asyncio.fixture
async def client(db_session):
    """Provide a test client with overridden database dependency."""
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            yield ac
    finally:
        app.dependency_overrides.clear()
