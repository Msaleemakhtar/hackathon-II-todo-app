"""Pytest configuration and fixtures for Phase III backend tests."""
import asyncio
import os
from typing import AsyncGenerator, Generator

import pytest
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel

from app.database import get_session
from app.models.task import TaskPhaseIII
from app.models.conversation import Conversation
from app.models.message import Message

# Load environment variables
load_dotenv()

# Test database URL (use PostgreSQL test database from .env)
TEST_DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL",
    "postgresql+asyncpg://neondb_owner:npg_zTkq1ABHR8uC@ep-mute-tooth-adbf0l4h-pooler.c-2.us-east-1.aws.neon.tech/neondb"
)


@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="function")
async def test_engine():
    """Create a test database engine."""
    engine = create_async_engine(
        TEST_DATABASE_URL,
        echo=False,
        future=True,
    )

    # Create all tables
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

    yield engine

    # Drop all tables
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)

    await engine.dispose()


@pytest.fixture(scope="function")
async def test_session(test_engine) -> AsyncGenerator[AsyncSession, None]:
    """Create a test database session."""
    async_session_maker = sessionmaker(
        test_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    async with async_session_maker() as session:
        yield session


@pytest.fixture(scope="function")
def override_get_session(test_session: AsyncSession):
    """Override the get_session dependency for testing."""

    async def _get_test_session():
        yield test_session

    return _get_test_session
