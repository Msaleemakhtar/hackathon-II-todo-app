import logging

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt

from app.config import settings

logger = logging.getLogger(__name__)
security = HTTPBearer()


async def verify_jwt(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> str:
    """
    Verify JWT token and extract user_id.

    Args:
        credentials: HTTP Bearer token from request header

    Returns:
        str: user_id from JWT payload

    Raises:
        HTTPException: 401 if token invalid or expired
    """
    token = credentials.credentials

    try:
        # Decode JWT token
        payload = jwt.decode(
            token,
            settings.better_auth_secret,
            algorithms=["HS256"],
        )

        # Extract user_id from payload
        user_id: str = payload.get("sub")
        if user_id is None:
            logger.warning("JWT validation failed: Missing 'sub' claim in token payload")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )

        return user_id

    except JWTError as e:
        logger.warning(f"JWT validation failed: {type(e).__name__} - {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        ) from None


async def verify_jwt_from_header(auth_header: str) -> str:
    """
    Extract and validate JWT from Authorization header string.

    This function is designed for use with ChatKit adapter where we need
    to manually extract the JWT from the raw Authorization header.

    Args:
        auth_header: Raw Authorization header value (e.g., "Bearer <token>")

    Returns:
        str: user_id from JWT payload

    Raises:
        HTTPException: 401 if header format invalid or token invalid
    """
    if not auth_header or not auth_header.startswith("Bearer "):
        logger.warning("Invalid Authorization header format")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Authorization header format",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Extract token from "Bearer <token>"
    token = auth_header.replace("Bearer ", "")

    try:
        # Decode JWT token
        payload = jwt.decode(
            token,
            settings.better_auth_secret,
            algorithms=["HS256"],
        )

        # Extract user_id from payload
        user_id: str = payload.get("sub")
        if user_id is None:
            logger.warning("JWT validation failed: Missing 'sub' claim in token payload")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )

        return user_id

    except JWTError as e:
        logger.warning(f"JWT validation failed: {type(e).__name__} - {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        ) from None


async def validate_user_id_match(path_user_id: str, jwt_user_id: str) -> None:
    """
    Validate that path user_id matches JWT user_id.

    Args:
        path_user_id: user_id from URL path parameter
        jwt_user_id: user_id from JWT token

    Raises:
        HTTPException: 403 if user_ids don't match
    """
    if path_user_id != jwt_user_id:
        logger.warning(
            f"User ID mismatch detected: path_user_id={path_user_id}, jwt_user_id={jwt_user_id}"
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User ID mismatch - cannot access another user's data",
        )
