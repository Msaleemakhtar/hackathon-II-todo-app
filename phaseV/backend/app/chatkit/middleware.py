"""
Authentication middleware for ChatKit SDK integration.

Extracts JWT from request headers and creates context dict with user_id.
"""

import logging
from typing import Any

from fastapi import HTTPException, Request

from app.dependencies.auth import verify_jwt_from_header

logger = logging.getLogger(__name__)


async def extract_user_context(request: Request) -> dict[str, Any]:
    """
    Extract user_id from JWT and return ChatKit context.

    This function is called by ChatKit SDK for every request to create the
    context dict that will be passed to:
    - All Store methods (save_thread, load_thread, save_item, load_items)
    - The respond() method in TaskChatServer

    Args:
        request: FastAPI Request object

    Returns:
        Context dict with user_id and request

    Raises:
        HTTPException: 401 if Authorization header is missing or invalid

    Flow:
        1. Extract Authorization header from request
        2. Validate JWT using existing verify_jwt_from_header()
        3. Extract user_id from token
        4. Return context dict with user_id
    """
    # Extract Authorization header
    auth_header = request.headers.get("Authorization")
    if not auth_header:
        logger.warning("Missing Authorization header in ChatKit request")
        raise HTTPException(
            status_code=401,
            detail="Missing Authorization header"
        )

    try:
        # Reuse existing JWT validation from auth.py:59-112
        # This function:
        # - Validates Bearer format
        # - Decodes JWT with BETTER_AUTH_SECRET
        # - Extracts user_id from 'sub' claim
        # - Raises 401 on JWTError
        user_id = await verify_jwt_from_header(auth_header)

        logger.info(f"User authenticated: user_id={user_id}")

        # Return context dict that will be passed to Store and respond()
        return {
            "user_id": user_id,
            "request": request,
        }

    except HTTPException:
        # Re-raise 401 from verify_jwt_from_header
        raise
    except Exception as e:
        logger.error(f"Unexpected error in extract_user_context: {str(e)}")
        raise HTTPException(
            status_code=401,
            detail="Authentication failed"
        ) from e
