"""Rate limiting dependency for API endpoints."""
from typing import Optional
from fastapi import HTTPException, Request, status
from fastapi.responses import JSONResponse
import time

from app.core.redis import get_redis, RATE_LIMIT_WINDOW, RATE_LIMIT_MAX_REQUESTS


class RateLimitException(HTTPException):
    """Custom exception for rate limit exceeded."""
    def __init__(self, retry_after: int):
        super().__init__(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded. Please try again later."
        )
        self.retry_after = retry_after


async def check_rate_limit(site_id: int, request: Request) -> dict:
    """
    Check if the site has exceeded the rate limit for sync operations.
    
    Args:
        site_id: The ID of the site
        request: The FastAPI request object
        
    Returns:
        dict: Rate limit information including remaining requests
        
    Raises:
        RateLimitException: If rate limit is exceeded
    """
    redis_client = await get_redis()
    
    # Create rate limit key
    rate_limit_key = f"rate_limit:site:{site_id}:sync"
    
    # Get current timestamp
    current_time = int(time.time())
    window_start = current_time - RATE_LIMIT_WINDOW
    
    # Remove old entries outside the window
    await redis_client.zremrangebyscore(rate_limit_key, 0, window_start)
    
    # Count requests in current window
    request_count = await redis_client.zcard(rate_limit_key)
    
    # Check if limit exceeded
    if request_count >= RATE_LIMIT_MAX_REQUESTS:
        # Get oldest request time to calculate retry-after
        oldest_requests = await redis_client.zrange(
            rate_limit_key, 0, 0, withscores=True
        )
        if oldest_requests:
            oldest_time = int(oldest_requests[0][1])
            retry_after = oldest_time + RATE_LIMIT_WINDOW - current_time
            
            # Set rate limit headers
            request.state.rate_limit_limit = RATE_LIMIT_MAX_REQUESTS
            request.state.rate_limit_remaining = 0
            request.state.rate_limit_reset = oldest_time + RATE_LIMIT_WINDOW
            request.state.rate_limit_retry_after = retry_after
            
            raise RateLimitException(retry_after=retry_after)
    
    # Add current request to the window
    await redis_client.zadd(rate_limit_key, {str(current_time): current_time})
    
    # Set expiry on the key
    await redis_client.expire(rate_limit_key, RATE_LIMIT_WINDOW)
    
    # Calculate rate limit info
    remaining = RATE_LIMIT_MAX_REQUESTS - request_count - 1
    reset_time = current_time + RATE_LIMIT_WINDOW
    
    # Store rate limit info in request state for middleware
    request.state.rate_limit_limit = RATE_LIMIT_MAX_REQUESTS
    request.state.rate_limit_remaining = remaining
    request.state.rate_limit_reset = reset_time
    
    return {
        "limit": RATE_LIMIT_MAX_REQUESTS,
        "remaining": remaining,
        "reset": reset_time
    }


async def rate_limit_middleware(request: Request, call_next):
    """
    Middleware to add rate limit headers to responses.
    """
    response = await call_next(request)
    
    # Add rate limit headers if they exist in request state
    if hasattr(request.state, "rate_limit_limit"):
        response.headers["X-RateLimit-Limit"] = str(request.state.rate_limit_limit)
        response.headers["X-RateLimit-Remaining"] = str(request.state.rate_limit_remaining)
        response.headers["X-RateLimit-Reset"] = str(request.state.rate_limit_reset)
        
        if hasattr(request.state, "rate_limit_retry_after"):
            response.headers["Retry-After"] = str(request.state.rate_limit_retry_after)
    
    return response