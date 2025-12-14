"""Tests for reminder management endpoints."""

import pytest
from datetime import datetime, timedelta, timezone
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from src.models.user import User
from src.models.task import Task
from src.models.category import Category
from src.models.reminder import Reminder
from test_utils import create_test_token
import uuid


@pytest.mark.asyncio
@pytest.mark.api
@pytest.mark.reminders
async def test_create_reminder(client: AsyncClient, db_session: AsyncSession):
    """Test creating a reminder for a task."""
    # Create test user
    user_id = str(uuid.uuid4())
    user = User(
        id=user_id,
        email=f"test_{user_id}@example.com",
        password_hash="$2b$12$KSHB23E5J4F321KLMIOPQR987654321ABCDEFGHIJKLMNOPQRSTUVWXYZ",
        name="Test User"
    )
    db_session.add(user)

    # Create default categories
    priority_category = Category(
        name="medium",
        type="priority",
        color="#FFFF00",
        is_default=True,
        user_id=user.id
    )
    status_category = Category(
        name="pending",
        type="status",
        color="#FFFF00",
        is_default=True,
        user_id=user.id
    )
    db_session.add(priority_category)
    db_session.add(status_category)

    # Create a task
    task = Task(
        title="Test Task",
        user_id=user.id,
        priority="medium",
        status="pending"
    )
    db_session.add(task)
    await db_session.commit()
    await db_session.refresh(task)

    # Create test token
    token = create_test_token(user.id, user.email, user.name)

    # Prepare reminder data
    remind_at = datetime.now(timezone.utc) + timedelta(hours=24)
    reminder_data = {
        "task_id": task.id,
        "remind_at": remind_at.isoformat(),
        "channel": "email"
    }

    # Create reminder
    response = await client.post(
        f"/api/v1/users/{user.id}/reminders",
        json=reminder_data,
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 201
    data = response.json()
    assert data["task_id"] == task.id
    assert data["channel"] == "email"
    assert data["is_sent"] == False


@pytest.mark.asyncio
@pytest.mark.api
@pytest.mark.reminders
async def test_list_reminders(client: AsyncClient, db_session: AsyncSession):
    """Test listing all reminders for a user."""
    # Create test user
    user_id = str(uuid.uuid4())
    user = User(
        id=user_id,
        email=f"test_{user_id}@example.com",
        password_hash="$2b$12$KSHB23E5J4F321KLMIOPQR987654321ABCDEFGHIJKLMNOPQRSTUVWXYZ",
        name="Test User"
    )
    db_session.add(user)

    # Create default categories and task
    priority_category = Category(
        name="medium",
        type="priority",
        color="#FFFF00",
        is_default=True,
        user_id=user.id
    )
    status_category = Category(
        name="pending",
        type="status",
        color="#FFFF00",
        is_default=True,
        user_id=user.id
    )
    db_session.add(priority_category)
    db_session.add(status_category)

    task = Task(
        title="Test Task",
        user_id=user.id,
        priority="medium",
        status="pending"
    )
    db_session.add(task)
    await db_session.commit()
    await db_session.refresh(task)

    # Create reminders
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    reminder1 = Reminder(
        task_id=task.id,
        user_id=user.id,
        remind_at=now + timedelta(hours=1),
        channel="email",
        is_sent=False
    )
    reminder2 = Reminder(
        task_id=task.id,
        user_id=user.id,
        remind_at=now - timedelta(hours=1),
        channel="browser",
        is_sent=True
    )
    db_session.add(reminder1)
    db_session.add(reminder2)
    await db_session.commit()

    # Create test token
    token = create_test_token(user.id, user.email, user.name)

    # Get upcoming reminders only
    response = await client.get(
        f"/api/v1/users/{user.id}/reminders?upcoming_only=true",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["is_sent"] == False

    # Get all reminders
    response = await client.get(
        f"/api/v1/users/{user.id}/reminders?upcoming_only=false",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2


@pytest.mark.asyncio
@pytest.mark.api
@pytest.mark.reminders
async def test_cancel_reminder(client: AsyncClient, db_session: AsyncSession):
    """Test canceling a reminder."""
    # Create test user
    user_id = str(uuid.uuid4())
    user = User(
        id=user_id,
        email=f"test_{user_id}@example.com",
        password_hash="$2b$12$KSHB23E5J4F321KLMIOPQR987654321ABCDEFGHIJKLMNOPQRSTUVWXYZ",
        name="Test User"
    )
    db_session.add(user)

    # Create default categories and task
    priority_category = Category(
        name="medium",
        type="priority",
        color="#FFFF00",
        is_default=True,
        user_id=user.id
    )
    status_category = Category(
        name="pending",
        type="status",
        color="#FFFF00",
        is_default=True,
        user_id=user.id
    )
    db_session.add(priority_category)
    db_session.add(status_category)

    task = Task(
        title="Test Task",
        user_id=user.id,
        priority="medium",
        status="pending"
    )
    db_session.add(task)
    await db_session.commit()
    await db_session.refresh(task)

    # Create reminder
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    reminder = Reminder(
        task_id=task.id,
        user_id=user.id,
        remind_at=now + timedelta(hours=1),
        channel="email",
        is_sent=False
    )
    db_session.add(reminder)
    await db_session.commit()
    await db_session.refresh(reminder)

    # Create test token
    token = create_test_token(user.id, user.email, user.name)

    # Cancel reminder
    response = await client.delete(
        f"/api/v1/users/{user.id}/reminders/{reminder.id}",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 204


@pytest.mark.asyncio
@pytest.mark.api
@pytest.mark.reminders
@pytest.mark.auth
async def test_reminder_access_control(client: AsyncClient, db_session: AsyncSession):
    """Test that users cannot access other users' reminders."""
    # Create two users
    user1_id = str(uuid.uuid4())
    user1 = User(
        id=user1_id,
        email=f"test_{user1_id}@example.com",
        password_hash="$2b$12$KSHB23E5J4F321KLMIOPQR987654321ABCDEFGHIJKLMNOPQRSTUVWXYZ",
        name="Test User 1"
    )
    user2_id = str(uuid.uuid4())
    user2 = User(
        id=user2_id,
        email=f"test_{user2_id}@example.com",
        password_hash="$2b$12$KSHB23E5J4F321KLMIOPQR987654321ABCDEFGHIJKLMNOPQRSTUVWXYZ",
        name="Test User 2"
    )
    db_session.add(user1)
    db_session.add(user2)
    await db_session.commit()

    # Create token for user1 but try to access user2's reminders
    token = create_test_token(user1.id, user1.email, user1.name)

    # Try to list user2's reminders with user1's token
    response = await client.get(
        f"/api/v1/users/{user2.id}/reminders",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 403
