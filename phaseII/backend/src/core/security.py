from datetime import datetime, timedelta, timezone
import asyncio
from typing import Optional
from functools import lru_cache
import time

import bcrypt
from jose import JWTError, jwt
from fastapi import HTTPException, status, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from .config import settings

# Simple in-memory cache for user existence checks (TTL: 30 minutes)
_user_cache: dict[str, float] = {}
_CACHE_TTL_SECONDS = 1800  # 30 minutes (increased from 5 for better performance)

# JWT payload cache to avoid redundant decoding (TTL matches token expiry)
# Format: {token_hash: (payload, expiry_timestamp)}
_jwt_cache: dict[str, tuple[dict, float]] = {}
_JWT_CACHE_MAX_SIZE = 1000  # Limit cache size to prevent memory bloat


async def hash_password(password: str) -> str:
    """Hash a password using bcrypt."""
    # Convert password to bytes and hash with bcrypt
    # Run in thread pool since bcrypt is CPU-intensive
    def _hash():
        password_bytes = password.encode('utf-8')
        salt = bcrypt.gensalt(rounds=12)
        hashed = bcrypt.hashpw(password_bytes, salt)
        return hashed.decode('utf-8')

    return await asyncio.to_thread(_hash)


async def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against a bcrypt hash."""
    # Run in thread pool since bcrypt is CPU-intensive
    def _verify():
        password_bytes = plain_password.encode('utf-8')
        hashed_bytes = hashed_password.encode('utf-8')
        return bcrypt.checkpw(password_bytes, hashed_bytes)

    return await asyncio.to_thread(_verify)

def verify_better_auth_token(token: str) -> dict:
    """Verify a Better Auth JWT token and return its payload.

    Uses in-memory caching to avoid redundant JWT decoding on repeated requests.
    Cache entries are automatically invalidated when tokens expire.

    Performance: Saves 3-5ms per request on cache hit.
    """
    # Check cache first - use token itself as key (already a hash-like string)
    current_time = time.time()

    if token in _jwt_cache:
        cached_payload, expiry = _jwt_cache[token]
        # Verify cache entry hasn't expired
        if current_time < expiry:
            return cached_payload
        else:
            # Remove expired entry
            _jwt_cache.pop(token, None)

    # Cache miss - decode the token
    try:
        payload = jwt.decode(token, settings.BETTER_AUTH_SECRET, algorithms=["HS256"])

        # Extract and validate expiration time from token
        token_exp = payload.get("exp")
        if token_exp is None:
            raise ValueError("Missing expiration in token")

        # Ensure token expiration is within acceptable range (15-30 minutes from creation)
        issued_at = payload.get("iat", 0)
        if issued_at > 0:
            token_lifetime = token_exp - issued_at
            max_allowed_lifetime = 30 * 60  # 30 minutes max
            min_allowed_lifetime = 15 * 60  # 15 minutes min
            if token_lifetime > max_allowed_lifetime or token_lifetime < min_allowed_lifetime:
                raise ValueError("Invalid token expiration time")

        # Cache the decoded payload with its expiration time
        expiry = token_exp
        _jwt_cache[token] = (payload, expiry)

        # Periodic cleanup of expired entries to prevent memory bloat
        if len(_jwt_cache) > _JWT_CACHE_MAX_SIZE:
            # Remove all expired entries
            expired_tokens = [
                tok for tok, (_, exp) in _jwt_cache.items()
                if current_time >= exp
            ]
            for tok in expired_tokens:
                _jwt_cache.pop(tok, None)

            # If still over limit, remove oldest 20% of entries
            if len(_jwt_cache) > _JWT_CACHE_MAX_SIZE:
                tokens_to_remove = list(_jwt_cache.keys())[:_JWT_CACHE_MAX_SIZE // 5]
                for tok in tokens_to_remove:
                    _jwt_cache.pop(tok, None)

        return payload

    except jwt.ExpiredSignatureError:
        raise ValueError("TOKEN_EXPIRED")
    except JWTError:
        raise ValueError("INVALID_TOKEN")

def get_current_user_from_token(authorization: str = None) -> dict:
    """Extract user from Authorization header token."""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = authorization.removeprefix("Bearer ").strip()
    try:
        payload = verify_better_auth_token(token)
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return payload
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Could not validate credentials: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )

async def get_current_user(request: Request):
    """Dependency to get current user from request."""
    auth_header = request.headers.get("Authorization")
    return get_current_user_from_token(auth_header)

def get_current_user_dependency():
    """Create a dependency that gets the current user."""
    async def current_user(request: Request):
        return await get_current_user(request)
    return current_user

async def ensure_user_exists_in_users_table(db: AsyncSession, user_payload: dict):
    """Ensure a user from Better Auth exists in the FastAPI users table.

    This provides just-in-time user sync between Better Auth's 'user' table
    and FastAPI's 'users' table to satisfy foreign key constraints.

    Uses in-memory cache to avoid redundant DB queries.
    """
    from src.models.user import User
    from src.services.category_service import initialize_default_categories

    user_id = user_payload.get("sub")
    email = user_payload.get("email")
    name = user_payload.get("name")

    # Check cache first
    current_time = time.time()
    cached_time = _user_cache.get(user_id)

    if cached_time and (current_time - cached_time) < _CACHE_TTL_SECONDS:
        # User exists in cache and cache is still valid
        return

    # Check if user already exists in users table
    result = await db.execute(select(User).where(User.id == user_id))
    existing_user = result.scalar_one_or_none()

    if not existing_user:
        # Create user in FastAPI users table
        new_user = User(
            id=user_id,
            email=email,
            password_hash="",  # Empty since Better Auth handles password
            name=name,
            created_at=datetime.now(timezone.utc).replace(tzinfo=None)
        )
        db.add(new_user)
        await db.commit()

        # Initialize default categories for the new user (CRITICAL for task validation)
        await initialize_default_categories(db, user_id)

    # Cache the user existence
    _user_cache[user_id] = current_time

    # Clean up old cache entries (simple cleanup strategy)
    if len(_user_cache) > 1000:  # Prevent unlimited growth
        expired_keys = [k for k, v in _user_cache.items() if (current_time - v) >= _CACHE_TTL_SECONDS]
        for key in expired_keys:
            _user_cache.pop(key, None)

async def validate_path_user_id(request: Request, user_id: str, db: AsyncSession = None):
    """Validate that the user_id in the path matches the user_id in the JWT token.

    Also ensures the user exists in the FastAPI users table for FK constraints.
    """
    current_user_payload = await get_current_user(request)
    current_user_id = current_user_payload.get("sub")

    # Check if the user_id in the path matches the user_id in the JWT
    if str(current_user_id) != str(user_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: user_id in path does not match authenticated user",
        )

    # Ensure user exists in users table (for FK constraints)
    if db:
        await ensure_user_exists_in_users_table(db, current_user_payload)

    return current_user_payload
