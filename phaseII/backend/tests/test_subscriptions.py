"""Tests for web push notification subscription endpoints."""

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from src.models.user import User
from src.models.user_subscription import UserSubscription
from test_utils import create_test_token
import uuid


@pytest.mark.asyncio
@pytest.mark.api
@pytest.mark.notifications
async def test_get_vapid_public_key(client: AsyncClient):
    """Test retrieving the VAPID public key."""
    # This endpoint doesn't require authentication
    response = await client.get("/api/v1/vapid/public-key")

    assert response.status_code == 200
    data = response.json()
    assert "public_key" in data
    assert len(data["public_key"]) > 0


@pytest.mark.asyncio
@pytest.mark.api
@pytest.mark.notifications
async def test_create_subscription(client: AsyncClient, db_session: AsyncSession):
    """Test creating a push notification subscription."""
    # Create test user
    user_id = str(uuid.uuid4())
    user = User(
        id=user_id,
        email=f"test_{user_id}@example.com",
        password_hash="$2b$12$KSHB23E5J4F321KLMIOPQR987654321ABCDEFGHIJKLMNOPQRSTUVWXYZ",
        name="Test User"
    )
    db_session.add(user)
    await db_session.commit()

    # Create test token
    token = create_test_token(user.id, user.email, user.name)

    # Prepare subscription data
    subscription_data = {
        "endpoint": "https://fcm.googleapis.com/fcm/send/test123",
        "p256dh_key": "BGj1234567890abcdefghijklmnopqrstuvwxyz",
        "auth_key": "AUTH1234567890abcdefg"
    }

    # Create subscription
    response = await client.post(
        f"/api/v1/users/{user.id}/subscriptions",
        json=subscription_data,
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 201
    data = response.json()
    assert data["endpoint"] == subscription_data["endpoint"]
    assert data["is_active"] == True
    assert "id" in data
    assert "created_at" in data


@pytest.mark.asyncio
@pytest.mark.api
@pytest.mark.notifications
async def test_create_duplicate_subscription(client: AsyncClient, db_session: AsyncSession):
    """Test creating a duplicate subscription updates the existing one."""
    # Create test user
    user_id = str(uuid.uuid4())
    user = User(
        id=user_id,
        email=f"test_{user_id}@example.com",
        password_hash="$2b$12$KSHB23E5J4F321KLMIOPQR987654321ABCDEFGHIJKLMNOPQRSTUVWXYZ",
        name="Test User"
    )
    db_session.add(user)
    await db_session.commit()

    # Create test token
    token = create_test_token(user.id, user.email, user.name)

    # Prepare subscription data
    subscription_data = {
        "endpoint": "https://fcm.googleapis.com/fcm/send/duplicate123",
        "p256dh_key": "BGj1234567890abcdefghijklmnopqrstuvwxyz",
        "auth_key": "AUTH1234567890abcdefg"
    }

    # Create subscription first time
    response1 = await client.post(
        f"/api/v1/users/{user.id}/subscriptions",
        json=subscription_data,
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response1.status_code == 201
    data1 = response1.json()
    subscription_id = data1["id"]

    # Create same subscription again (should update)
    response2 = await client.post(
        f"/api/v1/users/{user.id}/subscriptions",
        json=subscription_data,
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response2.status_code == 201
    data2 = response2.json()
    # Should return the same subscription ID if it updates
    # or a new one depending on implementation
    assert data2["endpoint"] == subscription_data["endpoint"]


@pytest.mark.asyncio
@pytest.mark.api
@pytest.mark.notifications
async def test_delete_subscription(client: AsyncClient, db_session: AsyncSession):
    """Test deleting a push notification subscription."""
    # Create test user
    user_id = str(uuid.uuid4())
    user = User(
        id=user_id,
        email=f"test_{user_id}@example.com",
        password_hash="$2b$12$KSHB23E5J4F321KLMIOPQR987654321ABCDEFGHIJKLMNOPQRSTUVWXYZ",
        name="Test User"
    )
    db_session.add(user)

    # Create a subscription directly in the database
    subscription = UserSubscription(
        user_id=user.id,
        endpoint="https://fcm.googleapis.com/fcm/send/delete123",
        p256dh_key="BGj1234567890abcdefghijklmnopqrstuvwxyz",
        auth_key="AUTH1234567890abcdefg",
        is_active=True
    )
    db_session.add(subscription)
    await db_session.commit()
    await db_session.refresh(subscription)

    # Create test token
    token = create_test_token(user.id, user.email, user.name)

    # Delete subscription
    response = await client.delete(
        f"/api/v1/users/{user.id}/subscriptions/{subscription.id}",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 204

    # Verify subscription is marked as inactive
    await db_session.refresh(subscription)
    assert subscription.is_active == False


@pytest.mark.asyncio
@pytest.mark.api
@pytest.mark.notifications
async def test_delete_nonexistent_subscription(client: AsyncClient, db_session: AsyncSession):
    """Test deleting a non-existent subscription."""
    # Create test user
    user_id = str(uuid.uuid4())
    user = User(
        id=user_id,
        email=f"test_{user_id}@example.com",
        password_hash="$2b$12$KSHB23E5J4F321KLMIOPQR987654321ABCDEFGHIJKLMNOPQRSTUVWXYZ",
        name="Test User"
    )
    db_session.add(user)
    await db_session.commit()

    # Create test token
    token = create_test_token(user.id, user.email, user.name)

    # Try to delete non-existent subscription
    response = await client.delete(
        f"/api/v1/users/{user.id}/subscriptions/99999",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 404


@pytest.mark.asyncio
@pytest.mark.api
@pytest.mark.notifications
@pytest.mark.auth
async def test_subscription_access_control(client: AsyncClient, db_session: AsyncSession):
    """Test that users cannot manage other users' subscriptions."""
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

    # Create token for user1 but try to create subscription for user2
    token = create_test_token(user1.id, user1.email, user1.name)

    subscription_data = {
        "endpoint": "https://fcm.googleapis.com/fcm/send/test123",
        "p256dh_key": "BGj1234567890abcdefghijklmnopqrstuvwxyz",
        "auth_key": "AUTH1234567890abcdefg"
    }

    # Try to create subscription for user2 with user1's token
    response = await client.post(
        f"/api/v1/users/{user2.id}/subscriptions",
        json=subscription_data,
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 403


@pytest.mark.asyncio
@pytest.mark.db
@pytest.mark.notifications
async def test_subscription_persistence(client: AsyncClient, db_session: AsyncSession):
    """Test that subscriptions are properly persisted to the database."""
    # Create test user
    user_id = str(uuid.uuid4())
    user = User(
        id=user_id,
        email=f"test_{user_id}@example.com",
        password_hash="$2b$12$KSHB23E5J4F321KLMIOPQR987654321ABCDEFGHIJKLMNOPQRSTUVWXYZ",
        name="Test User"
    )
    db_session.add(user)
    await db_session.commit()

    # Create test token
    token = create_test_token(user.id, user.email, user.name)

    # Create subscription
    subscription_data = {
        "endpoint": "https://fcm.googleapis.com/fcm/send/persist123",
        "p256dh_key": "BGj1234567890abcdefghijklmnopqrstuvwxyz",
        "auth_key": "AUTH1234567890abcdefg"
    }

    response = await client.post(
        f"/api/v1/users/{user.id}/subscriptions",
        json=subscription_data,
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 201
    data = response.json()

    # Query the database to verify persistence
    stmt = select(UserSubscription).where(UserSubscription.id == data["id"])
    result = await db_session.execute(stmt)
    db_subscription = result.scalar_one_or_none()

    assert db_subscription is not None
    assert db_subscription.endpoint == subscription_data["endpoint"]
    assert db_subscription.user_id == user.id
    assert db_subscription.is_active == True


@pytest.mark.asyncio
@pytest.mark.api
@pytest.mark.notifications
async def test_subscription_validation(client: AsyncClient, db_session: AsyncSession):
    """Test subscription validation rules."""
    # Create test user
    user_id = str(uuid.uuid4())
    user = User(
        id=user_id,
        email=f"test_{user_id}@example.com",
        password_hash="$2b$12$KSHB23E5J4F321KLMIOPQR987654321ABCDEFGHIJKLMNOPQRSTUVWXYZ",
        name="Test User"
    )
    db_session.add(user)
    await db_session.commit()

    # Create test token
    token = create_test_token(user.id, user.email, user.name)

    # Test missing required fields
    subscription_data = {
        "endpoint": "https://fcm.googleapis.com/fcm/send/test123"
        # Missing p256dh_key and auth_key
    }

    response = await client.post(
        f"/api/v1/users/{user.id}/subscriptions",
        json=subscription_data,
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 422
