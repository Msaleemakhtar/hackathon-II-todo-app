"""Tests for tag operations using PostgreSQL test database."""

import pytest
from httpx import AsyncClient
import uuid
from src.models.user import User
from src.models.tag import Tag
from test_utils import create_test_token


@pytest.mark.asyncio
async def test_create_tag(client: AsyncClient, db_session):
    """Test creating a new tag."""
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
    
    # Prepare tag creation data
    tag_data = {
        "name": "work",
        "color": "#FF0000"
    }

    # Make request to create a tag with proper authorization
    headers = {"Authorization": f"Bearer {token}"}
    response = await client.post(f"/api/v1/{user.id}/tags", json=tag_data, headers=headers)
    
    # Should return 201 Created with the new tag data
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == tag_data["name"]
    assert data["color"] == tag_data["color"]
    assert data["user_id"] == user.id


@pytest.mark.asyncio
async def test_get_tag(client: AsyncClient, db_session):
    """Test retrieving a specific tag."""
    # Create a test user in the database
    user_id = str(uuid.uuid4())
    user = User(
        id=user_id,
        email=f"test_{user_id}@example.com",
        password_hash="$2b$12$KSHB23E5J4F321KLMIOPQR987654321ABCDEFGHIJKLMNOPQRSTUVWXYZ",  # bcrypt hash
        name="Test User"
    )
    db_session.add(user)
    
    # Create a test tag
    tag = Tag(
        name="personal",
        color="#00FF00",
        user_id=user.id
    )
    db_session.add(tag)
    await db_session.commit()
    await db_session.refresh(tag)

    # Create a valid test JWT token
    token = create_test_token(user.id, user.email, user.name)
    
    # Make request to get the specific tag with proper authorization
    headers = {"Authorization": f"Bearer {token}"}
    response = await client.get(f"/api/v1/{user.id}/tags/{tag.id}", headers=headers)
    
    # Should return 200 OK with the tag data
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == tag.id
    assert data["name"] == tag.name
    assert data["color"] == tag.color
    assert data["user_id"] == user.id


@pytest.mark.asyncio
async def test_update_tag(client: AsyncClient, db_session):
    """Test updating an existing tag."""
    # Create a test user in the database
    user_id = str(uuid.uuid4())
    user = User(
        id=user_id,
        email=f"test_{user_id}@example.com",
        password_hash="$2b$12$KSHB23E5J4F321KLMIOPQR987654321ABCDEFGHIJKLMNOPQRSTUVWXYZ",  # bcrypt hash
        name="Test User"
    )
    db_session.add(user)
    
    # Create a test tag
    tag = Tag(
        name="original",
        color="#0000FF",
        user_id=user.id
    )
    db_session.add(tag)
    await db_session.commit()
    await db_session.refresh(tag)

    # Create a valid test JWT token
    token = create_test_token(user.id, user.email, user.name)
    
    # Prepare tag update data
    update_data = {
        "name": "updated",
        "color": "#FFFF00"
    }

    # Make request to update the tag with proper authorization
    headers = {"Authorization": f"Bearer {token}"}
    response = await client.put(f"/api/v1/{user.id}/tags/{tag.id}", json=update_data, headers=headers)
    
    # Should return 200 OK with the updated tag data
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == tag.id
    assert data["name"] == update_data["name"]
    assert data["color"] == update_data["color"]
    assert data["user_id"] == user.id


@pytest.mark.asyncio
async def test_partial_update_tag(client: AsyncClient, db_session):
    """Test partially updating an existing tag."""
    # Create a test user in the database
    user_id = str(uuid.uuid4())
    user = User(
        id=user_id,
        email=f"test_{user_id}@example.com",
        password_hash="$2b$12$KSHB23E5J4F321KLMIOPQR987654321ABCDEFGHIJKLMNOPQRSTUVWXYZ",  # bcrypt hash
        name="Test User"
    )
    db_session.add(user)
    
    # Create a test tag
    tag = Tag(
        name="original",
        color="#0000FF",
        user_id=user.id
    )
    db_session.add(tag)
    await db_session.commit()
    await db_session.refresh(tag)

    # Create a valid test JWT token
    token = create_test_token(user.id, user.email, user.name)
    
    # Prepare partial tag update data
    update_data = {
        "name": "partially_updated"
    }

    # Make request to partially update the tag with proper authorization
    headers = {"Authorization": f"Bearer {token}"}
    response = await client.patch(f"/api/v1/{user.id}/tags/{tag.id}", json=update_data, headers=headers)
    
    # Should return 200 OK with the updated tag data
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == tag.id
    assert data["name"] == update_data["name"]
    # Other fields should remain unchanged
    assert data["color"] == tag.color
    assert data["user_id"] == user.id


@pytest.mark.asyncio
async def test_delete_tag(client: AsyncClient, db_session):
    """Test deleting an existing tag."""
    # Create a test user in the database
    user_id = str(uuid.uuid4())
    user = User(
        id=user_id,
        email=f"test_{user_id}@example.com",
        password_hash="$2b$12$KSHB23E5J4F321KLMIOPQR987654321ABCDEFGHIJKLMNOPQRSTUVWXYZ",  # bcrypt hash
        name="Test User"
    )
    db_session.add(user)
    
    # Create a test tag
    tag = Tag(
        name="tag_to_delete",
        color="#FF0000",
        user_id=user.id
    )
    db_session.add(tag)
    await db_session.commit()
    await db_session.refresh(tag)

    # Create a valid test JWT token
    token = create_test_token(user.id, user.email, user.name)
    
    # Make request to delete the tag with proper authorization
    headers = {"Authorization": f"Bearer {token}"}
    response = await client.delete(f"/api/v1/{user.id}/tags/{tag.id}", headers=headers)
    
    # Should return 204 No Content
    assert response.status_code == 204
    
    # Verify the tag was actually deleted by trying to get it
    response = await client.get(f"/api/v1/{user.id}/tags/{tag.id}", headers=headers)
    # Should return 404 Not Found
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_list_tags(client: AsyncClient, db_session):
    """Test listing tags for a user."""
    # Create a test user in the database
    user_id = str(uuid.uuid4())
    user = User(
        id=user_id,
        email=f"test_{user_id}@example.com",
        password_hash="$2b$12$KSHB23E5J4F321KLMIOPQR987654321ABCDEFGHIJKLMNOPQRSTUVWXYZ",  # bcrypt hash
        name="Test User"
    )
    db_session.add(user)
    
    # Create multiple test tags for the user
    tag1 = Tag(
        name="work",
        color="#FF0000",
        user_id=user.id
    )
    tag2 = Tag(
        name="personal",
        color="#00FF00",
        user_id=user.id
    )
    db_session.add(tag1)
    db_session.add(tag2)
    await db_session.commit()
    await db_session.refresh(tag1)
    await db_session.refresh(tag2)

    # Create a valid test JWT token
    token = create_test_token(user.id, user.email, user.name)
    
    # Make request to list tags with proper authorization
    headers = {"Authorization": f"Bearer {token}"}
    response = await client.get(f"/api/v1/{user.id}/tags", headers=headers)
    
    # Should return 200 OK with the tags data
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)  # Direct list of tags
    assert len(data) >= 2  # Should have at least the 2 tags we created
    
    # Check that our tags are in the response
    tag_names = [tag["name"] for tag in data]
    assert tag1.name in tag_names
    assert tag2.name in tag_names