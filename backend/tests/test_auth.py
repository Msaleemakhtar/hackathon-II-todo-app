from datetime import datetime, timedelta, UTC

import pytest
from httpx import AsyncClient
from jose import jwt
from sqlalchemy.future import select

from src.core.config import settings
from src.core.database import get_db
from src.core.security import create_access_token
from src.models import User


@pytest.mark.asyncio
async def test_register_user_success(client: AsyncClient, db_session):
    """Test successful user registration."""
    response = await client.post(
        "/api/v1/auth/register",
        json={
            "email": "test@example.com",
            "password": "testpass123",
            "name": "Test User",
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "test@example.com"
    assert "id" in data
    assert "created_at" in data
    assert data["name"] == "Test User"

    # Verify user is in database
    result = await db_session.execute(
        select(User).where(User.email == "test@example.com")
    )
    user = result.scalar_one_or_none()
    assert user is not None
    assert user.email == "test@example.com"


@pytest.mark.asyncio
async def test_register_duplicate_email(client: AsyncClient):
    """Test registration with a duplicate email."""
    # Register first user
    await client.post(
        "/api/v1/auth/register",
        json={"email": "duplicate@example.com", "password": "testpass123"},
    )

    # Try to register again with same email
    response = await client.post(
        "/api/v1/auth/register",
        json={"email": "duplicate@example.com", "password": "anotherpassword"},
    )
    assert response.status_code == 400
    data = response.json()
    assert data["code"] == "EMAIL_ALREADY_EXISTS"


@pytest.mark.asyncio
async def test_register_short_password(client: AsyncClient):
    """Test registration with a password that is too short."""
    response = await client.post(
        "/api/v1/auth/register",
        json={"email": "shortpass@example.com", "password": "short"},
    )
    assert response.status_code == 422  # Pydantic validation error
    data = response.json()
    assert data["detail"][0]["msg"] == "String should have at least 8 characters"


@pytest.mark.asyncio
async def test_login_success(client: AsyncClient):
    """Test successful user login."""
    # Register a user first
    await client.post(
        "/api/v1/auth/register",
        json={"email": "login@example.com", "password": "loginpass123"},
    )

    response = await client.post(
        "/api/v1/auth/login",
        data={"username": "login@example.com", "password": "loginpass123"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert "refresh_token" in response.cookies


@pytest.mark.asyncio
async def test_login_invalid_credentials(client: AsyncClient):
    """Test login with invalid credentials."""
    # Register a user first
    await client.post(
        "/api/v1/auth/register",
        json={"email": "invalidlogin@example.com", "password": "validpassword"},
    )

    # Test with wrong password
    response = await client.post(
        "/api/v1/auth/login",
        data={"username": "invalidlogin@example.com", "password": "wrongpassword"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert response.status_code == 401
    data = response.json()
    assert data["code"] == "INVALID_CREDENTIALS"

    # Test with non-existent email
    response = await client.post(
        "/api/v1/auth/login",
        data={"username": "nonexistent@example.com", "password": "anypassword"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert response.status_code == 401
    data = response.json()
    assert data["code"] == "INVALID_CREDENTIALS"


@pytest.mark.asyncio
async def test_get_current_user_success(client: AsyncClient, db_session):
    """Test retrieving the current authenticated user."""
    # Register a user
    user_email = "me@example.com"
    user_password = "securepassword"
    user_name = "Auth Me"
    await client.post(
        "/api/v1/auth/register",
        json={"email": user_email, "password": user_password, "name": user_name},
    )

    # Fetch the user from the database to get the generated ID
    result = await db_session.execute(select(User).where(User.email == user_email))
    user = result.scalar_one_or_none()
    assert user is not None

    # Manually create an access token for the registered user
    access_token = create_access_token(user.id, user.email)

    response = await client.get(
        "/api/v1/auth/me", headers={"Authorization": f"Bearer {access_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == user_email
    assert data["id"] == user.id
    assert data["name"] == user_name


@pytest.mark.asyncio
async def test_get_current_user_no_token(client: AsyncClient):
    """Test retrieving current user without providing a token."""
    response = await client.get("/api/v1/auth/me")
    assert response.status_code == 401
    data = response.json()
    assert data["detail"] == "Not authenticated"


@pytest.mark.asyncio
async def test_get_current_user_invalid_token(client: AsyncClient):
    """Test retrieving current user with an invalid token."""
    response = await client.get(
        "/api/v1/auth/me", headers={"Authorization": "Bearer invalidtoken"}
    )
    assert response.status_code == 401
    data = response.json()
    assert data["detail"] == "INVALID_TOKEN"


@pytest.mark.asyncio
async def test_get_current_user_expired_token(client: AsyncClient, db_session):
    """Test retrieving current user with an expired token."""
    # Register a user
    user_email = "expired@example.com"
    user_password = "securepassword"
    await client.post(
        "/api/v1/auth/register", json={"email": user_email, "password": user_password}
    )

    # Fetch user to get ID
    result = await db_session.execute(select(User).where(User.email == user_email))
    user = result.scalar_one_or_none()

    # Manually create an expired token (by setting expire to a past time)
    now = datetime.now(UTC)
    expired_payload = {
        "sub": user.id,
        "email": user.email,
        "exp": now - timedelta(minutes=1),
        "iat": now - timedelta(minutes=5),
        "type": "access",
    }
    expired_token = jwt.encode(
        expired_payload, settings.JWT_SECRET_KEY, algorithm="HS256"
    )

    response = await client.get(
        "/api/v1/auth/me", headers={"Authorization": f"Bearer {expired_token}"}
    )
    assert response.status_code == 401
    data = response.json()
    assert data["detail"] == "TOKEN_EXPIRED"


@pytest.mark.asyncio
async def test_refresh_token_success(client: AsyncClient):
    """Test successful refresh of an access token."""
    # Register and log in a user to get a refresh token
    user_email = "refresh@example.com"
    user_password = "refreshpassword"
    await client.post(
        "/api/v1/auth/register", json={"email": user_email, "password": user_password}
    )
    login_response = await client.post(
        "/api/v1/auth/login",
        data={"username": user_email, "password": user_password},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    refresh_token = login_response.cookies.get("refresh_token")
    assert refresh_token is not None

    # Request new access token using the refresh token
    response = await client.post(
        "/api/v1/auth/refresh", cookies={"refresh_token": refresh_token}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    # Ensure no new refresh token is set in cookie (current design)
    assert "refresh_token" not in response.cookies


@pytest.mark.asyncio
async def test_refresh_token_expired(client: AsyncClient, db_session):
    """Test refreshing an access token with an expired refresh token."""
    # Register user
    user_email = "refresh_expired@example.com"
    user_password = "password"
    await client.post(
        "/api/v1/auth/register", json={"email": user_email, "password": user_password}
    )

    # Fetch user to get ID
    result = await db_session.execute(select(User).where(User.email == user_email))
    user = result.scalar_one_or_none()

    # Manually create an expired refresh token
    now = datetime.now(UTC)
    expired_refresh_payload = {
        "sub": user.id,
        "email": user.email,
        "exp": now - timedelta(days=1),  # Expired 1 day ago
        "iat": now - timedelta(days=2),
        "type": "refresh",
    }
    expired_refresh_token = jwt.encode(
        expired_refresh_payload, settings.JWT_SECRET_KEY, algorithm="HS256"
    )

    response = await client.post(
        "/api/v1/auth/refresh", cookies={"refresh_token": expired_refresh_token}
    )
    assert response.status_code == 401
    data = response.json()
    assert data["code"] == "REFRESH_TOKEN_EXPIRED"
    assert data["detail"] == "Refresh token has expired. Please log in again"


@pytest.mark.asyncio
async def test_refresh_token_invalid(client: AsyncClient):
    """Test refreshing an access token with an invalid refresh token."""
    response = await client.post(
        "/api/v1/auth/refresh", cookies={"refresh_token": "invalid.refresh.token"}
    )
    assert response.status_code == 401
    data = response.json()
    assert data["code"] == "INVALID_TOKEN"
    assert data["detail"] == "Invalid authentication token"


@pytest.mark.asyncio
async def test_refresh_token_missing(client: AsyncClient):
    """Test refreshing an access token without a refresh token cookie."""
    response = await client.post("/api/v1/auth/refresh")
    assert response.status_code == 401
    data = response.json()
    assert data["detail"] == "Missing refresh token"
    assert data["code"] == "MISSING_REFRESH_TOKEN"


@pytest.mark.asyncio
async def test_logout_success(client: AsyncClient):
    """Test successful user logout."""
    # Register and log in a user to get a refresh token
    user_email = "logout@example.com"
    user_password = "logoutpassword"
    await client.post(
        "/api/v1/auth/register", json={"email": user_email, "password": user_password}
    )
    login_response = await client.post(
        "/api/v1/auth/login",
        data={"username": user_email, "password": user_password},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert "refresh_token" in login_response.cookies

    # Perform logout
    logout_response = await client.post("/api/v1/auth/logout")
    assert logout_response.status_code == 200
    assert "message" in logout_response.json()
    assert logout_response.json()["message"] == "Successfully logged out"

    # Verify refresh_token cookie is cleared by checking Set-Cookie header
    set_cookie_header = logout_response.headers.get("set-cookie", "")
    assert "refresh_token" in set_cookie_header
    assert "Max-Age=0" in set_cookie_header or "max-age=0" in set_cookie_header
