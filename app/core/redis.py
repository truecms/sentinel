"""Redis client configuration."""

import logging
from typing import Optional

import redis.asyncio as redis

from app.core.config import settings

logger = logging.getLogger(__name__)

# Rate limiting constants
RATE_LIMIT_WINDOW = 3600  # 1 hour in seconds
RATE_LIMIT_MAX_REQUESTS = 100  # Maximum requests per window

# Cache TTL constants
CACHE_TTL_SHORT = 300  # 5 minutes in seconds
CACHE_TTL_MEDIUM = 600  # 10 minutes in seconds
MODULE_CACHE_TTL = 3600  # 1 hour in seconds
VERSION_CACHE_TTL = 3600  # 1 hour in seconds

# Global Redis client instance
_redis_client: Optional[redis.Redis] = None


async def get_redis_client() -> Optional[redis.Redis]:
    """Get Redis client instance."""
    global _redis_client

    if _redis_client is None:
        try:
            _redis_client = redis.Redis(
                host=settings.REDIS_HOST,
                port=settings.REDIS_PORT,
                db=settings.REDIS_DB,
                password=settings.REDIS_PASSWORD,
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5,
                socket_keepalive_options=30,
            )

            # Test connection
            await _redis_client.ping()
            logger.info("Redis connection established")

        except Exception as e:
            logger.warning(f"Redis connection failed: {e}")
            _redis_client = None

    return _redis_client


async def close_redis_client():
    """Close Redis client connection."""
    global _redis_client

    if _redis_client:
        await _redis_client.close()
        _redis_client = None
        logger.info("Redis connection closed")


async def get_redis() -> Optional[redis.Redis]:
    """Dependency to get Redis client."""
    return await get_redis_client()


async def close_redis_pool():
    """Close Redis connection pool (alias for compatibility)."""
    await close_redis_client()
