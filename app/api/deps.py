from typing import AsyncGenerator, Optional, Union
from pydantic import BaseModel

from fastapi import Depends, HTTPException, status, Request, Header
from fastapi.security import OAuth2PasswordBearer
from jose import jwt
from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.core.config import settings
from app.db.session import get_db as get_db_session
from app.models.user import User
from app.models.site import Site
from app.models.api_key import ApiKey
from app.schemas.user import UserResponse

class TokenData(BaseModel):
    sub: str

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/auth/access-token"
)

# Use the get_db from session.py
get_db = get_db_session

async def get_current_user(
    db: AsyncSession = Depends(get_db),
    token: str = Depends(oauth2_scheme)
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
    current_user: User = Depends(get_current_user)
) -> User:
    """Get current superuser."""
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    return current_user


async def authenticate_api_key(
    db: AsyncSession,
    api_key: str
) -> Union[User, Site]:
    """Authenticate using API key and return user or site."""
    # Hash the provided key
    key_hash = ApiKey.hash_key(api_key)
    
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
    token: Optional[str] = Depends(oauth2_scheme)
) -> Union[User, Site]:
    """Get current user or site based on JWT token or API key."""
    # Check for API key in headers first
    api_key = request.headers.get("X-API-Key") or request.headers.get("X-Site-Token")
    
    if api_key:
        return await authenticate_api_key(db, api_key)
    
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
    api_token: Optional[str] = Header(None, alias="X-API-Token")
) -> Site:
    """Get current site based on site UUID and API token (legacy) or API key."""
    # Try new API key authentication first
    api_key = request.headers.get("X-API-Key") or request.headers.get("X-Site-Token")
    
    if api_key:
        auth_result = await authenticate_api_key(db, api_key)
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
    token: Optional[str] = Depends(oauth2_scheme)
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
    current_user: User = Depends(get_current_user_flexible)
) -> User:
    """Get current superuser with flexible authentication."""
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    return current_user
