"""Redis connection and configuration module."""
import os
from typing import Optional
from redis import asyncio as redis
from redis.asyncio.connection import ConnectionPool

# Redis connection pool
_redis_pool: Optional[ConnectionPool] = None


async def get_redis_pool() -> ConnectionPool:
    """Get or create Redis connection pool."""
    global _redis_pool
    
    if _redis_pool is None:
        redis_host = os.getenv("REDIS_HOST", "localhost")
        redis_port = int(os.getenv("REDIS_PORT", 6379))
        
        _redis_pool = ConnectionPool(
            host=redis_host,
            port=redis_port,
            decode_responses=True,
            max_connections=50
        )
    
    return _redis_pool


async def get_redis() -> redis.Redis:
    """Get Redis client instance."""
    pool = await get_redis_pool()
    return redis.Redis(connection_pool=pool)


async def close_redis_pool():
    """Close Redis connection pool."""
    global _redis_pool
    if _redis_pool:
        await _redis_pool.disconnect()
        _redis_pool = None


# Rate limiting constants
RATE_LIMIT_WINDOW = 3600  # 1 hour in seconds
RATE_LIMIT_MAX_REQUESTS = 4  # Max requests per window

# Cache TTL constants
MODULE_CACHE_TTL = 3600  # 1 hour
VERSION_CACHE_TTL = 86400  # 24 hours