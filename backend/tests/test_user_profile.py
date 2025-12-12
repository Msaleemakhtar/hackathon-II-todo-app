"""Tests for user profile management endpoints using PostgreSQL test database."""

import pytest
from httpx import AsyncClient
import uuid
from src.models.user import User
from test_utils import create_test_token


@pytest.mark.asyncio
async def test_get_user_profile(client: AsyncClient, db_session):
    """Test retrieving user profile."""
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

    # Make request to get user profile with proper authorization
    headers = {"Authorization": f"Bearer {token}"}
    response = await client.get(f"/api/v1/{user.id}/profile", headers=headers)

    # Should return 200 OK with user profile data
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == user.id
    assert data["email"] == user.email
    assert data["name"] == user.name


@pytest.mark.asyncio
async def test_update_user_profile(client: AsyncClient, db_session):
    """Test updating user profile."""
    # Create a test user in the database
    user_id = str(uuid.uuid4())
    user = User(
        id=user_id,
        email=f"test_{user_id}@example.com",
        password_hash="$2b$12$KSHB23E5J4F321KLMIOPQR987654321ABCDEFGHIJKLMNOPQRSTUVWXYZ",  # bcrypt hash
        name="Original Name"
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    # Create a valid test JWT token
    token = create_test_token(user.id, user.email, user.name)

    # Prepare update data
    update_data = {
        "name": "Updated Name"
    }

    # Make request to update user profile with proper authorization
    headers = {"Authorization": f"Bearer {token}"}
    response = await client.patch(f"/api/v1/{user.id}/profile", json=update_data, headers=headers)

    # Should return 200 OK with updated user profile data
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == user.id
    assert data["email"] == user.email
    assert data["name"] == "Updated Name"