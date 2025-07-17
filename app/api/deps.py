import time
from typing import AsyncGenerator, Optional, Union

from fastapi import Depends, Header, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt
from pydantic import BaseModel, ValidationError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.config import settings
from app.core.redis import get_redis
from app.db.session import get_db as get_db_session
from app.models.api_key import ApiKey
from app.models.site import Site
from app.models.user import User
from app.schemas.user import UserResponse


class TokenData(BaseModel):
    sub: str


oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/auth/access-token",
    auto_error=False,  # Don't automatically raise error if no token
)

# Use the get_db from session.py
get_db = get_db_session


async def get_current_user(
    db: AsyncSession = Depends(get_db), token: str = Depends(oauth2_scheme)
) -> User:
    """Get current user based on JWT token."""
    try:
        payload = jwt.decode(
            token, settings.JWT_SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        token_data = TokenData(sub=payload.get("sub"))
    except (jwt.JWTError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Query for user by email with all relationships loaded
    query = (
        select(User)
        .where(User.email == token_data.sub)
        .options(selectinload(User.organizations))
    )
    result = await db.execute(query)
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Inactive user",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Ensure all attributes are loaded
    await db.refresh(user)

    return user


def get_current_active_superuser(
    current_user: User = Depends(get_current_user),
) -> User:
    """Get current superuser."""
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions"
        )
    return current_user


async def check_api_key_rate_limit(request: Request, api_key_hash: str) -> None:
    """Check rate limit for API key authentication attempts."""
    redis_client = await get_redis()

    # Create rate limit key based on IP and key hash
    client_ip = request.client.host if request.client else "unknown"
    rate_limit_key = f"rate_limit:api_auth:{client_ip}:{api_key_hash[:8]}"

    # Rate limit: 10 attempts per minute
    current_time = int(time.time())
    window_start = current_time - 60  # 1 minute window
    max_attempts = 10

    # Remove old entries outside the window
    await redis_client.zremrangebyscore(rate_limit_key, 0, window_start)

    # Count attempts in current window
    attempt_count = await redis_client.zcard(rate_limit_key)

    # Check if limit exceeded
    if attempt_count >= max_attempts:
        # Get oldest attempt time to calculate retry-after
        oldest_attempts = await redis_client.zrange(
            rate_limit_key, 0, 0, withscores=True
        )
        if oldest_attempts:
            oldest_time = int(oldest_attempts[0][1])
            retry_after = oldest_time + 60 - current_time

            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Too many authentication attempts. Please try again later.",
                headers={"Retry-After": str(retry_after)},
            )

    # Add current attempt to the window
    await redis_client.zadd(rate_limit_key, {str(current_time): current_time})

    # Set expiry on the key
    await redis_client.expire(rate_limit_key, 60)


async def authenticate_api_key(
    db: AsyncSession, api_key: str, request: Optional[Request] = None
) -> Union[User, Site]:
    """Authenticate using API key and return user or site."""
    # Hash the provided key
    key_hash = ApiKey.hash_key(api_key)

    # Check rate limit if request is provided
    if request:
        await check_api_key_rate_limit(request, key_hash)

    # Find the API key in database
    query = (
        select(ApiKey)
        .where(ApiKey.key_hash == key_hash)
        .options(selectinload(ApiKey.user), selectinload(ApiKey.site))
    )
    result = await db.execute(query)
    api_key_obj = result.scalar_one_or_none()

    if not api_key_obj:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Check if API key is valid (active and not expired)
    if not api_key_obj.is_valid():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key expired or inactive",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Update last used timestamp
    api_key_obj.update_last_used()
    await db.commit()

    # Return the associated user or site
    if api_key_obj.user_id:
        if not api_key_obj.user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User account is inactive",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return api_key_obj.user
    elif api_key_obj.site_id:
        if not api_key_obj.site.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Site is inactive",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return api_key_obj.site
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key not associated with user or site",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_user_or_site(
    request: Request,
    db: AsyncSession = Depends(get_db),
    token: Optional[str] = Depends(oauth2_scheme),
) -> Union[User, Site]:
    """Get current user or site based on JWT token or API key."""
    # Check for API key in headers first
    api_key = request.headers.get("X-API-Key") or request.headers.get("X-Site-Token")

    if api_key:
        return await authenticate_api_key(db, api_key, request)

    # Fall back to JWT authentication
    if token:
        return await get_current_user(db, token)

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Authentication required",
        headers={"WWW-Authenticate": "Bearer"},
    )


async def get_current_site(
    request: Request,
    db: AsyncSession = Depends(get_db),
    site_uuid: Optional[str] = Header(None, alias="X-Site-UUID"),
    api_token: Optional[str] = Header(None, alias="X-API-Token"),
) -> Site:
    """Get current site based on site UUID and API token (legacy) or API key."""
    # Try new API key authentication first
    api_key = request.headers.get("X-API-Key") or request.headers.get("X-Site-Token")

    if api_key:
        auth_result = await authenticate_api_key(db, api_key, request)
        if isinstance(auth_result, Site):
            return auth_result
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="API key is not associated with a site",
                headers={"WWW-Authenticate": "Bearer"},
            )

    # Fall back to legacy site UUID + API token authentication
    if site_uuid and api_token:
        query = (
            select(Site)
            .where(Site.site_uuid == site_uuid)
            .where(Site.api_token == api_token)
        )
        result = await db.execute(query)
        site = result.scalar_one_or_none()

        if not site:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid site credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )

        if not site.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Site is inactive",
                headers={"WWW-Authenticate": "Bearer"},
            )

        return site

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Site authentication required",
        headers={"WWW-Authenticate": "Bearer"},
    )


async def get_current_user_flexible(
    request: Request,
    db: AsyncSession = Depends(get_db),
    token: Optional[str] = Depends(oauth2_scheme),
) -> User:
    """Get current user with flexible authentication (JWT or API key)."""
    auth_result = await get_current_user_or_site(request, db, token)

    if isinstance(auth_result, User):
        return auth_result
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )


def get_current_active_superuser_flexible(
    current_user: User = Depends(get_current_user_flexible),
) -> User:
    """Get current superuser with flexible authentication."""
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions"
        )
    return current_user
