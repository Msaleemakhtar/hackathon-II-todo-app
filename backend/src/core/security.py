from datetime import datetime, timedelta, UTC
import asyncio

import bcrypt
from jose import JWTError, jwt

from .config import settings


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

def create_access_token(user_id: str, email: str) -> str:
    """Create a JWT access token (15 min expiry)."""
    now = datetime.now(UTC)
    expire = now + timedelta(minutes=15)
    payload = {
        "sub": user_id,
        "email": email,
        "exp": expire,
        "iat": now,
        "type": "access"
    }
    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm="HS256")

def create_refresh_token(user_id: str, email: str) -> str:
    """Create a JWT refresh token (7 day expiry)."""
    now = datetime.now(UTC)
    expire = now + timedelta(days=7)
    payload = {
        "sub": user_id,
        "email": email,
        "exp": expire,
        "iat": now,
        "type": "refresh"
    }
    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm="HS256")

def verify_token(token: str, expected_type: str = "access") -> dict:
    """Verify a JWT token and return its payload."""
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=["HS256"])
        if payload.get("type") != expected_type:
            raise ValueError(f"Invalid token type: expected {expected_type}")
        return payload
    except jwt.ExpiredSignatureError:
        raise ValueError("TOKEN_EXPIRED")
    except JWTError:
        raise ValueError("INVALID_TOKEN")
