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
