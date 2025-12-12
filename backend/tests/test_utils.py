"""Test utilities for the Todo App Backend."""

from datetime import datetime, timedelta, timezone
from jose import jwt
from src.core.config import settings


def create_test_token(user_id: str, email: str, name: str = "Test User") -> str:
    """Create a test JWT token with the specified user details that matches Better Auth format."""
    # Create token payload with required claims that match Better Auth expectations
    now = datetime.now(timezone.utc)
    payload = {
        "sub": user_id,           # Required: user ID
        "email": email,           # User's email
        "name": name,             # User's name
        "iat": int(now.timestamp()),  # Issued at timestamp (required for validation)
        "exp": int((now + timedelta(minutes=20)).timestamp()),  # Expiration (15-30 min requirement)
        "tokenType": "access"     # Better Auth access token type
    }

    # Encode the token using the same secret as the app
    token = jwt.encode(payload, settings.BETTER_AUTH_SECRET, algorithm="HS256")
    return token