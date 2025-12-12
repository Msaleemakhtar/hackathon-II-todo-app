"""Tests for task CRUD operations using PostgreSQL test database."""

import pytest
from httpx import AsyncClient
import uuid
from src.models.user import User
from src.models.task import Task
from src.models.category import Category
from test_utils import create_test_token


@pytest.mark.asyncio
async def test_create_task(client: AsyncClient, db_session):
    """Test creating a new task."""
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
    # These are needed for task validation
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
    await db_session.commit()
    await db_session.refresh(user)

    # Create a valid test JWT token
    token = create_test_token(user.id, user.email, user.name)
    
    # Prepare task creation data
    task_data = {
        "title": "Test Task",
        "description": "This is a test task",
        "priority": "medium",
        "status": "pending"
    }

    # Make request to create a task with proper authorization
    headers = {"Authorization": f"Bearer {token}"}
    response = await client.post(f"/api/v1/{user.id}/tasks", json=task_data, headers=headers)
    
    # Should return 201 Created with the new task data
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == task_data["title"]
    assert data["description"] == task_data["description"]
    assert data["priority"] == task_data["priority"]
    assert data["status"] == task_data["status"]
    assert data["user_id"] == user.id
    assert not data["completed"]  # pending status should result in completed=False


@pytest.mark.asyncio
async def test_get_task(client: AsyncClient, db_session):
    """Test retrieving a specific task."""
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
        name="high",
        type="priority",
        color="#FF0000",
        is_default=True,
        user_id=user.id
    )
    status_category = Category(
        name="completed",
        type="status",
        color="#00FF00",
        is_default=True,
        user_id=user.id
    )
    db_session.add(priority_category)
    db_session.add(status_category)
    
    # Create a test task
    task = Task(
        title="Existing Task",
        description="This is an existing task",
        priority="high",
        status="completed",
        completed=True,
        user_id=user.id
    )
    db_session.add(task)
    await db_session.commit()
    await db_session.refresh(task)

    # Create a valid test JWT token
    token = create_test_token(user.id, user.email, user.name)
    
    # Make request to get the specific task with proper authorization
    headers = {"Authorization": f"Bearer {token}"}
    response = await client.get(f"/api/v1/{user.id}/tasks/{task.id}", headers=headers)
    
    # Should return 200 OK with the task data
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == task.id
    assert data["title"] == task.title
    assert data["description"] == task.description
    assert data["priority"] == task.priority
    assert data["status"] == task.status
    assert data["completed"] == task.completed
    assert data["user_id"] == user.id


@pytest.mark.asyncio
async def test_update_task(client: AsyncClient, db_session):
    """Test updating an existing task."""
    # Create a test user in the database
    user_id = str(uuid.uuid4())
    user = User(
        id=user_id,
        email=f"test_{user_id}@example.com",
        password_hash="$2b$12$KSHB23E5J4F321KLMIOPQR987654321ABCDEFGHIJKLMNOPQRSTUVWXYZ",  # bcrypt hash
        name="Test User"
    )
    db_session.add(user)
    
    # Create all default categories for the user (mimicking what happens in user creation)
    priority_low = Category(
        name="low",
        type="priority",
        color="#FFFF00",
        is_default=True,
        user_id=user.id
    )
    priority_medium = Category(
        name="medium",
        type="priority",
        color="#FFFF00",
        is_default=True,
        user_id=user.id
    )
    priority_high = Category(
        name="high",
        type="priority",
        color="#FFFF00",
        is_default=True,
        user_id=user.id
    )
    status_not_started = Category(
        name="not_started",
        type="status",
        color="#FFFF00",
        is_default=True,
        user_id=user.id
    )
    status_pending = Category(
        name="pending",
        type="status",
        color="#FFFF00",
        is_default=True,
        user_id=user.id
    )
    status_in_progress = Category(
        name="in_progress",
        type="status",
        color="#FFFF00",
        is_default=True,
        user_id=user.id
    )
    status_completed = Category(
        name="completed",
        type="status",
        color="#FFFF00",
        is_default=True,
        user_id=user.id
    )
    db_session.add_all([
        priority_low, priority_medium, priority_high,
        status_not_started, status_pending, status_in_progress, status_completed
    ])

    # Create a test task
    task = Task(
        title="Original Task",
        description="This is the original task",
        priority="medium",
        status="pending",
        completed=False,
        user_id=user.id
    )
    db_session.add(task)
    await db_session.commit()
    await db_session.refresh(task)

    # Create a valid test JWT token
    token = create_test_token(user.id, user.email, user.name)

    # Prepare task update data
    update_data = {
        "title": "Updated Task Title",
        "description": "This is the updated task description",
        "priority": "high",
        "status": "completed",
        "completed": True  # This should be ignored, as completion is derived from status
    }

    # Make request to update the task with proper authorization
    headers = {"Authorization": f"Bearer {token}"}
    response = await client.put(f"/api/v1/{user.id}/tasks/{task.id}", json=update_data, headers=headers)

    # Should return 200 OK with the updated task data
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == task.id
    assert data["title"] == update_data["title"]
    assert data["description"] == update_data["description"]
    assert data["priority"] == update_data["priority"]
    assert data["status"] == update_data["status"]
    # 'completed' should be derived from status - completed status should make completed=True
    assert data["completed"] == True
    assert data["user_id"] == user.id


@pytest.mark.asyncio
async def test_partial_update_task(client: AsyncClient, db_session):
    """Test partially updating an existing task."""
    # Create a test user in the database
    user_id = str(uuid.uuid4())
    user = User(
        id=user_id,
        email=f"test_{user_id}@example.com",
        password_hash="$2b$12$KSHB23E5J4F321KLMIOPQR987654321ABCDEFGHIJKLMNOPQRSTUVWXYZ",  # bcrypt hash
        name="Test User"
    )
    db_session.add(user)

    # Create all default categories for the user (mimicking what happens in user creation)
    priority_low = Category(
        name="low",
        type="priority",
        color="#FFFF00",
        is_default=True,
        user_id=user.id
    )
    priority_medium = Category(
        name="medium",
        type="priority",
        color="#FFFF00",
        is_default=True,
        user_id=user.id
    )
    priority_high = Category(
        name="high",
        type="priority",
        color="#FFFF00",
        is_default=True,
        user_id=user.id
    )
    status_not_started = Category(
        name="not_started",
        type="status",
        color="#FFFF00",
        is_default=True,
        user_id=user.id
    )
    status_pending = Category(
        name="pending",
        type="status",
        color="#FFFF00",
        is_default=True,
        user_id=user.id
    )
    status_in_progress = Category(
        name="in_progress",
        type="status",
        color="#FFFF00",
        is_default=True,
        user_id=user.id
    )
    status_completed = Category(
        name="completed",
        type="status",
        color="#FFFF00",
        is_default=True,
        user_id=user.id
    )
    db_session.add_all([
        priority_low, priority_medium, priority_high,
        status_not_started, status_pending, status_in_progress, status_completed
    ])

    # Create a test task
    task = Task(
        title="Original Task",
        description="This is the original task",
        priority="medium",
        status="pending",
        completed=False,
        user_id=user.id
    )
    db_session.add(task)
    await db_session.commit()
    await db_session.refresh(task)

    # Create a valid test JWT token
    token = create_test_token(user.id, user.email, user.name)
    
    # Prepare partial task update data
    update_data = {
        "title": "Partially Updated Task"
    }

    # Make request to partially update the task with proper authorization
    headers = {"Authorization": f"Bearer {token}"}
    response = await client.patch(f"/api/v1/{user.id}/tasks/{task.id}", json=update_data, headers=headers)
    
    # Should return 200 OK with the updated task data
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == task.id
    assert data["title"] == update_data["title"]
    # Other fields should remain unchanged
    assert data["description"] == task.description
    assert data["priority"] == task.priority
    assert data["status"] == task.status
    assert data["user_id"] == user.id


@pytest.mark.asyncio
async def test_delete_task(client: AsyncClient, db_session):
    """Test deleting an existing task."""
    # Create a test user in the database
    user_id = str(uuid.uuid4())
    user = User(
        id=user_id,
        email=f"test_{user_id}@example.com",
        password_hash="$2b$12$KSHB23E5J4F321KLMIOPQR987654321ABCDEFGHIJKLMNOPQRSTUVWXYZ",  # bcrypt hash
        name="Test User"
    )
    db_session.add(user)

    # Create all default categories for the user (mimicking what happens in user creation)
    priority_low = Category(
        name="low",
        type="priority",
        color="#FFFF00",
        is_default=True,
        user_id=user.id
    )
    priority_medium = Category(
        name="medium",
        type="priority",
        color="#FFFF00",
        is_default=True,
        user_id=user.id
    )
    priority_high = Category(
        name="high",
        type="priority",
        color="#FFFF00",
        is_default=True,
        user_id=user.id
    )
    status_not_started = Category(
        name="not_started",
        type="status",
        color="#FFFF00",
        is_default=True,
        user_id=user.id
    )
    status_pending = Category(
        name="pending",
        type="status",
        color="#FFFF00",
        is_default=True,
        user_id=user.id
    )
    status_in_progress = Category(
        name="in_progress",
        type="status",
        color="#FFFF00",
        is_default=True,
        user_id=user.id
    )
    status_completed = Category(
        name="completed",
        type="status",
        color="#FFFF00",
        is_default=True,
        user_id=user.id
    )
    db_session.add_all([
        priority_low, priority_medium, priority_high,
        status_not_started, status_pending, status_in_progress, status_completed
    ])

    # Create a test task
    task = Task(
        title="Task to Delete",
        description="This task will be deleted",
        priority="medium",
        status="pending",
        completed=False,
        user_id=user.id
    )
    db_session.add(task)
    await db_session.commit()
    await db_session.refresh(task)

    # Create a valid test JWT token
    token = create_test_token(user.id, user.email, user.name)
    
    # Make request to delete the task with proper authorization
    headers = {"Authorization": f"Bearer {token}"}
    response = await client.delete(f"/api/v1/{user.id}/tasks/{task.id}", headers=headers)
    
    # Should return 204 No Content
    assert response.status_code == 204
    
    # Verify the task was actually deleted by trying to get it
    response = await client.get(f"/api/v1/{user.id}/tasks/{task.id}", headers=headers)
    # Should return 404 Not Found
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_list_tasks(client: AsyncClient, db_session):
    """Test listing tasks for a user."""
    # Create a test user in the database
    user_id = str(uuid.uuid4())
    user = User(
        id=user_id,
        email=f"test_{user_id}@example.com",
        password_hash="$2b$12$KSHB23E5J4F321KLMIOPQR987654321ABCDEFGHIJKLMNOPQRSTUVWXYZ",  # bcrypt hash
        name="Test User"
    )
    db_session.add(user)

    # Create all default categories for the user (mimicking what happens in user creation)
    priority_low = Category(
        name="low",
        type="priority",
        color="#FFFF00",
        is_default=True,
        user_id=user.id
    )
    priority_medium = Category(
        name="medium",
        type="priority",
        color="#FFFF00",
        is_default=True,
        user_id=user.id
    )
    priority_high = Category(
        name="high",
        type="priority",
        color="#FFFF00",
        is_default=True,
        user_id=user.id
    )
    status_not_started = Category(
        name="not_started",
        type="status",
        color="#FFFF00",
        is_default=True,
        user_id=user.id
    )
    status_pending = Category(
        name="pending",
        type="status",
        color="#FFFF00",
        is_default=True,
        user_id=user.id
    )
    status_in_progress = Category(
        name="in_progress",
        type="status",
        color="#FFFF00",
        is_default=True,
        user_id=user.id
    )
    status_completed = Category(
        name="completed",
        type="status",
        color="#FFFF00",
        is_default=True,
        user_id=user.id
    )
    db_session.add_all([
        priority_low, priority_medium, priority_high,
        status_not_started, status_pending, status_in_progress, status_completed
    ])
    await db_session.commit()

    # Create multiple test tasks for the user
    task1 = Task(
        title="First Task",
        description="Description for first task",
        priority="medium",
        status="pending",
        completed=False,
        user_id=user.id
    )
    task2 = Task(
        title="Second Task",
        description="Description for second task",
        priority="high",
        status="completed",
        completed=True,
        user_id=user.id
    )
    db_session.add(task1)
    db_session.add(task2)
    await db_session.commit()
    await db_session.refresh(task1)
    await db_session.refresh(task2)

    # Create a valid test JWT token
    token = create_test_token(user.id, user.email, user.name)
    
    # Make request to list tasks with proper authorization
    headers = {"Authorization": f"Bearer {token}"}
    response = await client.get(f"/api/v1/{user.id}/tasks", headers=headers)
    
    # Should return 200 OK with paginated task data
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert data["total"] >= 2  # Should have at least the 2 tasks we created
    assert data["page"] == 1
    assert data["limit"] == 20  # Default limit
    
    # Check that our tasks are in the response
    task_titles = [task["title"] for task in data["items"]]
    assert task1.title in task_titles
    assert task2.title in task_titles