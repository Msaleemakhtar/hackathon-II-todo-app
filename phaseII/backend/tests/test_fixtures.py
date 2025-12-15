"""Test fixtures for database models in the Todo App Backend."""

import pytest
import pytest_asyncio
from sqlmodel.ext.asyncio.session import AsyncSession
from src.models.user import User
from src.models.task import Task, TaskCreate
from src.models.tag import Tag, TagCreate
from src.models.category import Category, CategoryCreate
from datetime import datetime
import uuid


@pytest_asyncio.fixture
async def sample_user(db_session: AsyncSession) -> User:
    """Create a sample user for testing."""
    user = User(
        id=str(uuid.uuid4()),
        email=f"test_{user.id}@example.com",
        password_hash="$2b$12$KSHB23E5J4F321KLMIOPQR987654321ABCDEFGHIJKLMNOPQRSTUVWXYZ",  # bcrypt hash
        name="Test User"
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest_asyncio.fixture
async def sample_category(db_session: AsyncSession, sample_user: User) -> Category:
    """Create a sample category for testing."""
    category_data = CategoryCreate(
        name="high",
        type="priority",
        color="#FF0000"
    )
    category = Category(
        **category_data.model_dump(),
        user_id=sample_user.id
    )
    db_session.add(category)
    await db_session.commit()
    await db_session.refresh(category)
    return category


@pytest_asyncio.fixture
async def sample_task(db_session: AsyncSession, sample_user: User) -> Task:
    """Create a sample task for testing."""
    task_data = TaskCreate(
        title="Test Task",
        description="This is a test task",
        priority="medium",
        status="pending",
        user_id=sample_user.id
    )
    task = Task(
        **task_data.model_dump()
    )
    db_session.add(task)
    await db_session.commit()
    await db_session.refresh(task)
    return task


@pytest_asyncio.fixture
async def sample_tag(db_session: AsyncSession, sample_user: User) -> Tag:
    """Create a sample tag for testing."""
    tag_data = TagCreate(
        name="work",
        color="#00FF00"
    )
    tag = Tag(
        **tag_data.model_dump(),
        user_id=sample_user.id
    )
    db_session.add(tag)
    await db_session.commit()
    await db_session.refresh(tag)
    return tag