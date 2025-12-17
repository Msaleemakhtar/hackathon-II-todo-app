"""JWT token validation for Better Auth integration."""
from typing import Any

from jose import JWTError, jwt

from app.config import settings


class JWTValidationError(Exception):
    """Exception raised when JWT validation fails."""

    pass


def verify_token(token: str) -> dict[str, Any]:
    """
    Verify and decode JWT token from Better Auth.

    Args:
        token: JWT token string

    Returns:
        Dict containing token payload including user_id

    Raises:
        JWTValidationError: If token is invalid or expired
    """
    try:
        # Decode JWT token
        payload = jwt.decode(
            token,
            settings.BETTER_AUTH_SECRET,
            algorithms=["HS256"],
        )

        # Extract user_id from payload
        user_id: str | None = payload.get("sub")
        if not user_id:
            raise JWTValidationError("Token missing user ID (sub claim)")

        return payload

    except JWTError as e:
        raise JWTValidationError(f"Invalid token: {str(e)}") from e


def extract_user_id(token: str) -> str:
    """
    Extract user ID from JWT token.

    Args:
        token: JWT token string

    Returns:
        User ID string

    Raises:
        JWTValidationError: If token is invalid or missing user ID
    """
    payload = verify_token(token)
    user_id = payload.get("sub")
    if not user_id:
        raise JWTValidationError("Token missing user ID")
    return user_id
