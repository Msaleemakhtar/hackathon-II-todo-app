"""Tests for category operations using PostgreSQL test database."""

import pytest
from httpx import AsyncClient
import uuid
from src.models.user import User
from src.models.category import Category
from test_utils import create_test_token


@pytest.mark.asyncio
async def test_create_category(client: AsyncClient, db_session):
    """Test creating a new category."""
    # Create a test user in the database
    user_id = str(uuid.uuid4())
    user = User(
        id=user_id,
        email=f"test_{user_id}@example.com",
        password_hash="$2b$12$KSHB23E5J4F321KLMIOPQR987654321ABCDEFGHIJKLMNOPQRSTUVWXYZ",  # bcrypt hash
        name="Test User"
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    # Create a valid test JWT token
    token = create_test_token(user.id, user.email, user.name)
    
    # Prepare category creation data
    category_data = {
        "name": "high",
        "type": "priority",
        "color": "#FF0000"
    }

    # Make request to create a category with proper authorization
    headers = {"Authorization": f"Bearer {token}"}
    response = await client.post(f"/api/v1/{user.id}/categories", json=category_data, headers=headers)
    
    # Should return 201 Created with the new category data
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == category_data["name"]
    assert data["type"] == category_data["type"]
    assert data["color"] == category_data["color"]
    assert data["user_id"] == user.id


@pytest.mark.asyncio
async def test_get_categories_metadata(client: AsyncClient, db_session):
    """Test retrieving categories metadata (priorities and statuses)."""
    # Create a test user in the database
    user_id = str(uuid.uuid4())
    user = User(
        id=user_id,
        email=f"test_{user_id}@example.com",
        password_hash="$2b$12$KSHB23E5J4F321KLMIOPQR987654321ABCDEFGHIJKLMNOPQRSTUVWXYZ",  # bcrypt hash
        name="Test User"
    )
    db_session.add(user)
    
    # Create some test categories
    priority_category = Category(
        name="high",
        type="priority",
        color="#FF0000",
        user_id=user.id
    )
    status_category = Category(
        name="pending",
        type="status",
        color="#FFFF00",
        user_id=user.id
    )
    db_session.add(priority_category)
    db_session.add(status_category)
    await db_session.commit()
    await db_session.refresh(priority_category)
    await db_session.refresh(status_category)

    # Create a valid test JWT token
    token = create_test_token(user.id, user.email, user.name)
    
    # Make request to get categories metadata with proper authorization
    headers = {"Authorization": f"Bearer {token}"}
    response = await client.get(f"/api/v1/{user.id}/categories/metadata", headers=headers)
    
    # Should return 200 OK with priorities and statuses
    assert response.status_code == 200
    data = response.json()
    assert "priorities" in data
    assert "statuses" in data
    assert isinstance(data["priorities"], list)
    assert isinstance(data["statuses"], list)


@pytest.mark.asyncio
async def test_list_categories(client: AsyncClient, db_session):
    """Test listing categories for a user."""
    # Create a test user in the database
    user_id = str(uuid.uuid4())
    user = User(
        id=user_id,
        email=f"test_{user_id}@example.com",
        password_hash="$2b$12$KSHB23E5J4F321KLMIOPQR987654321ABCDEFGHIJKLMNOPQRSTUVWXYZ",  # bcrypt hash
        name="Test User"
    )
    db_session.add(user)
    
    # Create multiple test categories for the user
    category1 = Category(
        name="high",
        type="priority",
        color="#FF0000",
        user_id=user.id
    )
    category2 = Category(
        name="medium",
        type="priority",
        color="#FFFF00",
        user_id=user.id
    )
    category3 = Category(
        name="pending",
        type="status",
        color="#FFFF00",
        user_id=user.id
    )
    db_session.add(category1)
    db_session.add(category2)
    db_session.add(category3)
    await db_session.commit()
    await db_session.refresh(category1)
    await db_session.refresh(category2)
    await db_session.refresh(category3)

    # Create a valid test JWT token
    token = create_test_token(user.id, user.email, user.name)
    
    # Make request to list all categories with proper authorization
    headers = {"Authorization": f"Bearer {token}"}
    response = await client.get(f"/api/v1/{user.id}/categories", headers=headers)
    
    # Should return 200 OK with the categories data
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert isinstance(data["items"], list)
    assert len(data["items"]) >= 3  # Should have at least the 3 categories we created
    
    # Check that our categories are in the response
    category_names = [cat["name"] for cat in data["items"]]
    assert category1.name in category_names
    assert category2.name in category_names
    assert category3.name in category_names


@pytest.mark.asyncio
async def test_list_categories_by_type(client: AsyncClient, db_session):
    """Test listing categories for a user filtered by type."""
    # Create a test user in the database
    user_id = str(uuid.uuid4())
    user = User(
        id=user_id,
        email=f"test_{user_id}@example.com",
        password_hash="$2b$12$KSHB23E5J4F321KLMIOPQR987654321ABCDEFGHIJKLMNOPQRSTUVWXYZ",  # bcrypt hash
        name="Test User"
    )
    db_session.add(user)
    
    # Create multiple test categories for the user
    priority_category = Category(
        name="high",
        type="priority",
        color="#FF0000",
        user_id=user.id
    )
    status_category = Category(
        name="pending",
        type="status",
        color="#FFFF00",
        user_id=user.id
    )
    db_session.add(priority_category)
    db_session.add(status_category)
    await db_session.commit()
    await db_session.refresh(priority_category)
    await db_session.refresh(status_category)

    # Create a valid test JWT token
    token = create_test_token(user.id, user.email, user.name)
    
    # Make request to list priority categories with proper authorization
    headers = {"Authorization": f"Bearer {token}"}
    response = await client.get(f"/api/v1/{user.id}/categories?type=priority", headers=headers)
    
    # Should return 200 OK with the priority categories data
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert isinstance(data["items"], list)
    
    # All returned categories should be of type 'priority'
    for cat in data["items"]:
        assert cat["type"] == "priority"


@pytest.mark.asyncio
async def test_update_category(client: AsyncClient, db_session):
    """Test updating an existing category."""
    # Create a test user in the database
    user_id = str(uuid.uuid4())
    user = User(
        id=user_id,
        email=f"test_{user_id}@example.com",
        password_hash="$2b$12$KSHB23E5J4F321KLMIOPQR987654321ABCDEFGHIJKLMNOPQRSTUVWXYZ",  # bcrypt hash
        name="Test User"
    )
    db_session.add(user)
    
    # Create a test category
    category = Category(
        name="original",
        type="priority",
        color="#FF0000",
        user_id=user.id
    )
    db_session.add(category)
    await db_session.commit()
    await db_session.refresh(category)

    # Create a valid test JWT token
    token = create_test_token(user.id, user.email, user.name)
    
    # Prepare category update data
    update_data = {
        "name": "updated",
        "color": "#00FF00"
    }

    # Make request to update the category with proper authorization
    headers = {"Authorization": f"Bearer {token}"}
    response = await client.patch(f"/api/v1/{user.id}/categories/{category.id}", json=update_data, headers=headers)
    
    # Should return 200 OK with the updated category data
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == category.id
    assert data["name"] == update_data["name"]
    assert data["color"] == update_data["color"]
    assert data["user_id"] == user.id
    # Type should remain unchanged
    assert data["type"] == category.type


@pytest.mark.asyncio
async def test_delete_category(client: AsyncClient, db_session):
    """Test deleting an existing category."""
    # Create a test user in the database
    user_id = str(uuid.uuid4())
    user = User(
        id=user_id,
        email=f"test_{user_id}@example.com",
        password_hash="$2b$12$KSHB23E5J4F321KLMIOPQR987654321ABCDEFGHIJKLMNOPQRSTUVWXYZ",  # bcrypt hash
        name="Test User"
    )
    db_session.add(user)
    
    # Create a test category
    category = Category(
        name="to_delete",
        type="priority",
        color="#FF0000",
        user_id=user.id,
        is_default=False  # Make sure it's not a default category which can't be deleted
    )
    db_session.add(category)
    await db_session.commit()
    await db_session.refresh(category)

    # Create a valid test JWT token
    token = create_test_token(user.id, user.email, user.name)
    
    # Make request to delete the category with proper authorization
    headers = {"Authorization": f"Bearer {token}"}
    response = await client.delete(f"/api/v1/{user.id}/categories/{category.id}", headers=headers)
    
    # Should return 204 No Content
    assert response.status_code == 204
    
    # Verify the category was actually deleted by trying to list categories
    response = await client.get(f"/api/v1/{user.id}/categories", headers=headers)
    data = response.json()
    category_names = [cat["name"] for cat in data["items"]]
    assert category.name not in category_names