"""Redis client configuration."""

import logging
from typing import Optional

import redis.asyncio as redis

from app.core.config import settings

logger = logging.getLogger(__name__)

# Rate limiting constants
_ = 3600  # 1 hour in seconds
_ = 100  # Maximum requests per window

# Cache TTL constants
_ = 300  # 5 minutes in seconds
_ = 600  # 10 minutes in seconds

# Global Redis client instance
_redis_client: Optional[redis.Redis] = None


async def get_redis_client() -> Optional[redis.Redis]:
    """Get Redis client instance."""
    global _redis_client

    if _redis_client is None:
        try:
            _redis_client = redis.Redis(
                _=settings.REDIS_HOST,
                _=settings.REDIS_PORT,
                _=settings.REDIS_DB,
                _=settings.REDIS_PASSWORD,
                _=True,
                _=5,
                _=5,
                _=30,
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
        _ = None
        logger.info("Redis connection closed")


async def get_redis() -> Optional[redis.Redis]:
    """Dependency to get Redis client."""
    return await get_redis_client()


async def close_redis_pool():
    """Close Redis connection pool (alias for compatibility)."""
    await close_redis_client()
