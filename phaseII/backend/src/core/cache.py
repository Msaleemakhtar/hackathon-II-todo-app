"""Redis caching implementation for performance optimization."""
from typing import Any, Optional
from datetime import datetime, timedelta, timezone
import json

from aiocache import Cache
from aiocache.serializers import JsonSerializer
from sqlmodel import Field, SQLModel


class CacheEntry(SQLModel):
    """CacheEntry model for representing cached data (not a database table)."""

    cache_key: str
    cached_data: Any
    ttl_seconds: int
    created_at: datetime
    expires_at: datetime


class RedisCache:
    """Redis cache implementation with TTL and invalidation support."""

    def __init__(self, redis_url: str = "redis://localhost:6379"):
        """Initialize Redis cache.

        Args:
            redis_url: Redis connection URL
        """
        self.cache = Cache(
            Cache.REDIS,
            endpoint=redis_url.split("//")[1].split(":")[0],
            port=int(redis_url.split(":")[-1]) if ":" in redis_url.split("//")[1] else 6379,
            serializer=JsonSerializer(),
        )

    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache.

        Args:
            key: Cache key

        Returns:
            Cached value or None if not found or expired
        """
        return await self.cache.get(key)

    async def set(
        self, key: str, value: Any, ttl: int = 3600
    ) -> None:
        """Set value in cache with TTL.

        Args:
            key: Cache key
            value: Value to cache
            ttl: Time-to-live in seconds (default: 1 hour)
        """
        await self.cache.set(key, value, ttl=ttl)

    async def delete(self, key: str) -> None:
        """Delete value from cache.

        Args:
            key: Cache key to delete
        """
        await self.cache.delete(key)

    async def delete_pattern(self, pattern: str) -> None:
        """Delete all keys matching pattern.

        Args:
            pattern: Pattern to match (e.g., "user:123:*")
        """
        try:
            # Get the underlying Redis client from aiocache
            redis_client = await self.cache._get_client()

            # Scan for keys matching the pattern
            cursor = 0
            while True:
                cursor, keys = await redis_client.scan(cursor, match=pattern, count=100)
                if keys:
                    # Delete matched keys
                    await redis_client.delete(*keys)
                if cursor == 0:
                    break
        except Exception as e:
            # Log error but don't fail - fallback to full cache clear if pattern deletion fails
            print(f"Error deleting cache pattern '{pattern}': {e}")
            # Optionally fallback to clearing all cache (not recommended for production)
            # await self.clear()

    async def clear(self) -> None:
        """Clear all cached data."""
        await self.cache.clear()

    async def exists(self, key: str) -> bool:
        """Check if key exists in cache.

        Args:
            key: Cache key to check

        Returns:
            True if key exists, False otherwise
        """
        return await self.cache.exists(key)

    def get_cache_key(self, namespace: str, *args: Any) -> str:
        """Generate cache key from namespace and arguments.

        Args:
            namespace: Cache namespace (e.g., "tasks", "users")
            *args: Additional key components

        Returns:
            Cache key string
        """
        components = [namespace] + [str(arg) for arg in args]
        return ":".join(components)


# Cache configuration for different data types
CACHE_TTL_CONFIG = {
    "tasks": 300,  # 5 minutes
    "user_tasks": 300,  # 5 minutes
    "task_details": 600,  # 10 minutes
    "user_profile": 3600,  # 1 hour
    "categories": 86400,  # 24 hours (rarely changes)
    "tags": 86400,  # 24 hours (rarely changes)
}


def get_ttl(cache_type: str) -> int:
    """Get TTL for cache type.

    Args:
        cache_type: Type of cached data

    Returns:
        TTL in seconds
    """
    return CACHE_TTL_CONFIG.get(cache_type, 3600)  # Default: 1 hour
