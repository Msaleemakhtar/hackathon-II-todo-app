"""Integration tests for task-tag associations using PostgreSQL test database."""

import pytest
from httpx import AsyncClient
import uuid
from src.models.user import User
from src.models.task import Task
from src.models.tag import Tag
from src.models.category import Category
from test_utils import create_test_token


@pytest.mark.asyncio
async def test_associate_tag_with_task(client: AsyncClient, db_session):
    """Test associating a tag with a task."""
    # Create a test user in the database
    user_id = str(uuid.uuid4())
    user = User(
        id=user_id,
        email=f"test_{user_id}@example.com",
        password_hash="$2b$12$KSHB23E5J4F321KLMIOPQR987654321ABCDEFGHIJKLMNOPQRSTUVWXYZ",  # bcrypt hash
        name="Test User"
    )
    db_session.add(user)
    
    # Create default categories for the user
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
    
    # Create a test task
    task = Task(
        title="Test Task",
        description="This is a test task",
        priority="medium",
        status="pending",
        completed=False,
        user_id=user.id
    )
    
    # Create a test tag
    tag = Tag(
        name="work",
        color="#FF0000",
        user_id=user.id
    )
    
    db_session.add(task)
    db_session.add(tag)
    await db_session.commit()
    await db_session.refresh(task)
    await db_session.refresh(tag)

    # Create a valid test JWT token
    token = create_test_token(user.id, user.email, user.name)
    
    # Make request to associate the tag with the task
    headers = {"Authorization": f"Bearer {token}"}
    response = await client.post(f"/api/v1/{user.id}/tasks/{task.id}/tags/{tag.id}", headers=headers)
    
    # Should return 201 Created with the updated task data
    assert response.status_code == 201
    data = response.json()
    assert data["id"] == task.id
    assert data["title"] == task.title
    # Check that the tag is associated with the task
    tag_ids = [t["id"] for t in data["tags"]]
    assert tag.id in tag_ids


@pytest.mark.asyncio
async def test_dissociate_tag_from_task(client: AsyncClient, db_session):
    """Test dissociating a tag from a task."""
    # Create a test user in the database
    user_id = str(uuid.uuid4())
    user = User(
        id=user_id,
        email=f"test_{user_id}@example.com",
        password_hash="$2b$12$KSHB23E5J4F321KLMIOPQR987654321ABCDEFGHIJKLMNOPQRSTUVWXYZ",  # bcrypt hash
        name="Test User"
    )
    db_session.add(user)
    
    # Create default categories for the user
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
    
    # Create a test task
    task = Task(
        title="Test Task",
        description="This is a test task",
        priority="medium",
        status="pending",
        completed=False,
        user_id=user.id
    )
    
    # Create a test tag
    tag = Tag(
        name="work",
        color="#FF0000",
        user_id=user.id
    )
    
    db_session.add(task)
    db_session.add(tag)
    await db_session.commit()
    await db_session.refresh(task)
    await db_session.refresh(tag)

    # Create a valid test JWT token
    token = create_test_token(user.id, user.email, user.name)
    
    # First, associate the tag with the task
    headers = {"Authorization": f"Bearer {token}"}
    response = await client.post(f"/api/v1/{user.id}/tasks/{task.id}/tags/{tag.id}", headers=headers)
    assert response.status_code == 201
    
    # Now, dissociate the tag from the task
    response = await client.delete(f"/api/v1/{user.id}/tasks/{task.id}/tags/{tag.id}", headers=headers)
    
    # Should return 204 No Content
    assert response.status_code == 204
    
    # Verify the tag was dissociated by getting the task again
    response = await client.get(f"/api/v1/{user.id}/tasks/{task.id}", headers=headers)
    assert response.status_code == 200
    data = response.json()
    tag_ids = [t["id"] for t in data["tags"]]
    assert tag.id not in tag_ids


@pytest.mark.asyncio
async def test_task_filtering_by_tag(client: AsyncClient, db_session):
    """Test filtering tasks by tag."""
    # Create a test user in the database
    user_id = str(uuid.uuid4())
    user = User(
        id=user_id,
        email=f"test_{user_id}@example.com",
        password_hash="$2b$12$KSHB23E5J4F321KLMIOPQR987654321ABCDEFGHIJKLMNOPQRSTUVWXYZ",  # bcrypt hash
        name="Test User"
    )
    db_session.add(user)
    
    # Create default categories for the user
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
    
    # Create test tasks
    task1 = Task(
        title="Task with tag",
        description="This task has a tag",
        priority="medium",
        status="pending",
        completed=False,
        user_id=user.id
    )
    task2 = Task(
        title="Task without tag",
        description="This task has no tags",
        priority="low",
        status="pending",
        completed=False,
        user_id=user.id
    )
    
    # Create a test tag
    tag = Tag(
        name="important",
        color="#FF0000",
        user_id=user.id
    )
    
    db_session.add(task1)
    db_session.add(task2)
    db_session.add(tag)
    await db_session.commit()
    await db_session.refresh(task1)
    await db_session.refresh(task2)
    await db_session.refresh(tag)

    # Create a valid test JWT token
    token = create_test_token(user.id, user.email, user.name)
    
    # Associate tag with task1
    headers = {"Authorization": f"Bearer {token}"}
    response = await client.post(f"/api/v1/{user.id}/tasks/{task1.id}/tags/{tag.id}", headers=headers)
    assert response.status_code == 201

    # Now filter tasks by the tag
    response = await client.get(f"/api/v1/{user.id}/tasks?tag={tag.id}", headers=headers)
    assert response.status_code == 200
    data = response.json()
    
    # Should return only task1 (the one with the tag)
    returned_task_titles = [t["title"] for t in data["items"]]
    assert task1.title in returned_task_titles
    assert task2.title not in returned_task_titles