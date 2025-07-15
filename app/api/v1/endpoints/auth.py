from datetime import timedelta
from typing import Any
import logging

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.api import deps
from app.core import security
from app.core.config import settings
from app.models.user import User
from app.schemas.user import UserResponse
from pydantic import BaseModel
from app.models.organization import Organization
from app.models.user_organization import user_organization

# Configure logging
logger = logging.getLogger(__name__)

router = APIRouter()

class UserRegister(BaseModel):
    email: str
    password: str
    full_name: str
    organization_name: str

@router.post("/register", response_model=UserResponse)
async def register(
    user_data: UserRegister,
    db: AsyncSession = Depends(deps.get_db)
) -> Any:
    """Register a new user with their organization."""
    logger.info(f"Registration attempt for user: {user_data.email}")
    
    # Check if user already exists
    query = select(User).where(User.email == user_data.email)
    result = await db.execute(query)
    existing_user = result.scalar_one_or_none()
    
    if existing_user:
        logger.warning(f"User already exists: {user_data.email}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists"
        )
    
    # Check if organization already exists
    query = select(Organization).where(Organization.name == user_data.organization_name)
    result = await db.execute(query)
    organization = result.scalar_one_or_none()
    
    # Create organization if it doesn't exist
    if not organization:
        organization = Organization(
            name=user_data.organization_name,
            is_active=True
        )
        db.add(organization)
        await db.commit()
        await db.refresh(organization)
        logger.info(f"Created new organization: {user_data.organization_name}")
    
    # Create user
    user = User(
        email=user_data.email,
        full_name=user_data.full_name,
        hashed_password=security.get_password_hash(user_data.password),
        is_active=True,
        is_superuser=False,
        organization_id=organization.id,
        role="viewer"  # Default role for new users
    )
    
    db.add(user)
    await db.commit()
    await db.refresh(user)
    
    # Add user-organization association
    await db.execute(
        user_organization.insert().values(
            user_id=user.id,
            organization_id=organization.id
        )
    )
    await db.commit()
    
    logger.info(f"User registered successfully: {user_data.email}")
    return UserResponse.model_validate(user)

@router.post("/access-token")
async def login_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(deps.get_db)
) -> Any:
    """OAuth2 compatible token login, get an access token for future requests."""
    logger.info(f"Attempting login for user: {form_data.username}")
    
    # Query for the user
    query = select(User).where(User.email == form_data.username)
    result = await db.execute(query)
    user = result.scalar_one_or_none()
    
    if not user:
        logger.warning(f"User not found: {form_data.username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not security.verify_password(form_data.password, user.hashed_password):
        logger.warning(f"Password verification failed for user: {user.email}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    if not user.is_active:
        logger.warning(f"Inactive user attempted login: {user.email}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Inactive user",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    token = security.create_access_token(
        data={"sub": user.email},
        expires_delta=access_token_expires
    )
    
    logger.info(f"Login successful for user: {user.email}")
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": UserResponse.model_validate(user)
    }

@router.post("/test-token", response_model=UserResponse)
async def test_token(current_user: User = Depends(deps.get_current_user)) -> Any:
    """Test access token."""
    return UserResponse.model_validate(current_user)

class PasswordChange(BaseModel):
    current_password: str
    new_password: str

@router.post("/change-password")
async def change_password(
    password_data: PasswordChange,
    current_user: User = Depends(deps.get_current_user),
    db: AsyncSession = Depends(deps.get_db)
) -> Any:
    """Change user password."""
    logger.info(f"Password change attempt for user: {current_user.email}")
    
    if not security.verify_password(password_data.current_password, current_user.hashed_password):
        logger.warning(f"Invalid current password for user: {current_user.email}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid current password"
        )
    
    current_user.hashed_password = security.get_password_hash(password_data.new_password)
    db.add(current_user)
    await db.commit()
    await db.refresh(current_user)
    
    logger.info(f"Password changed successfully for user: {current_user.email}")
    return {"message": "Password changed successfully"}

@router.get("/me", response_model=UserResponse)
async def get_current_user(current_user: User = Depends(deps.get_current_user)) -> Any:
    """Get current user details."""
    logger.info(f"Getting details for user: {current_user.email}")
    return UserResponse.model_validate(current_user)
