import pytest
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from src.models import Tag, Task, TaskTagLink, User


@pytest.mark.asyncio
async def test_user_creation(db_session):
    """Test user model creation and constraints."""
    user = User(
        id="test-uuid",
        email="test@example.com",
        password_hash="hashed_password",
        name="Test User",
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    assert user.id == "test-uuid"
    assert user.email == "test@example.com"
    assert user.created_at is not None


@pytest.mark.asyncio
async def test_task_relationships(db_session):
    """Test task-user relationship and cascade delete."""
    user = User(id="user-1", email="user@example.com", password_hash="hash")
    task = Task(title="Test Task", user_id=user.id)

    db_session.add(user)
    db_session.add(task)
    await db_session.commit()

    # Verify relationship - eagerly load tasks
    result = await db_session.execute(
        select(User).options(selectinload(User.tasks)).where(User.id == user.id)
    )
    user = result.scalar_one()
    assert len(user.tasks) == 1
    assert user.tasks[0].title == "Test Task"

    # Test cascade delete
    await db_session.delete(user)
    await db_session.commit()
    # Task should be deleted (cascade)
    result = await db_session.execute(select(Task).where(Task.id == task.id))
    assert result.scalar_one_or_none() is None


@pytest.mark.asyncio
async def test_tag_relationships(db_session):
    """Test tag-user relationship and cascade delete."""
    user = User(id="user-2", email="user2@example.com", password_hash="hash")
    tag = Tag(name="Work", user_id=user.id)

    db_session.add(user)
    db_session.add(tag)
    await db_session.commit()

    # Verify relationship - eagerly load tags
    result = await db_session.execute(
        select(User).options(selectinload(User.tags)).where(User.id == user.id)
    )
    user = result.scalar_one()
    assert len(user.tags) == 1
    assert user.tags[0].name == "Work"

    await db_session.delete(user)
    await db_session.commit()
    result = await db_session.execute(select(Tag).where(Tag.id == tag.id))
    assert result.scalar_one_or_none() is None


@pytest.mark.asyncio
async def test_task_tag_link_relationships(db_session):
    """Test many-to-many relationship between Task and Tag."""
    user = User(id="user-3", email="user3@example.com", password_hash="hash")
    task = Task(title="Buy groceries", user_id=user.id)
    tag1 = Tag(name="Personal", user_id=user.id)
    tag2 = Tag(name="Urgent", user_id=user.id)

    db_session.add(user)
    db_session.add(task)
    db_session.add(tag1)
    db_session.add(tag2)
    await db_session.commit()
    await db_session.refresh(task)
    await db_session.refresh(tag1)
    await db_session.refresh(tag2)

    # Link task and tags
    task_tag_link1 = TaskTagLink(task_id=task.id, tag_id=tag1.id)
    task_tag_link2 = TaskTagLink(task_id=task.id, tag_id=tag2.id)

    db_session.add(task_tag_link1)
    db_session.add(task_tag_link2)
    await db_session.commit()

    # Eagerly load tags relationship
    result = await db_session.execute(
        select(Task).options(selectinload(Task.tags)).where(Task.id == task.id)
    )
    task = result.scalar_one()

    assert len(task.tags) == 2
    assert tag1 in task.tags
    assert tag2 in task.tags

    # Test cascade delete for link
    await db_session.delete(task)
    await db_session.commit()
    result = await db_session.execute(
        select(TaskTagLink).where(TaskTagLink.task_id == task.id)
    )
    assert result.scalar_one_or_none() is None
