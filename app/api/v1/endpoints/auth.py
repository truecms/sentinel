import logging
import secrets
import string
from datetime import datetime, timedelta
from typing import Any

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api import deps
from app.core import security
from app.core.config import settings
from app.models.organization import Organization
from app.models.user import User
from app.models.user_organization import user_organization
from app.schemas.user import UserResponse

# Configure logging
logger = logging.getLogger(__name__)

router = APIRouter()

# In-memory storage for password reset tokens (in production, use Redis or database)
password_reset_tokens = {}


class UserRegister(BaseModel):
    email: str
    password: str
    full_name: str
    organization_name: str


@router.post("/register", response_model=UserResponse)
async def register(
    user_data: UserRegister, db: AsyncSession = Depends(deps.get_db)
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
            detail="User with this email already exists",
        )

    # Check if organization already exists
    query = select(Organization).where(Organization.name == user_data.organization_name)
    result = await db.execute(query)
    organization = result.scalar_one_or_none()

    # Create organization if it doesn't exist
    if not organization:
        organization = Organization(name=user_data.organization_name, is_active=True)
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
        role="viewer",  # Default role for new users
    )

    db.add(user)
    await db.commit()
    await db.refresh(user)

    # Add user-organization association
    await db.execute(
        user_organization.insert().values(
            user_id=user.id, organization_id=organization.id
        )
    )
    await db.commit()

    logger.info(f"User registered successfully: {user_data.email}")
    return UserResponse.model_validate(user)


@router.post("/access-token")
async def login_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(deps.get_db),
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
        data={"sub": user.email}, expires_delta=access_token_expires
    )

    logger.info(f"Login successful for user: {user.email}")
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": UserResponse.model_validate(user),
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
    db: AsyncSession = Depends(deps.get_db),
) -> Any:
    """Change user password."""
    logger.info(f"Password change attempt for user: {current_user.email}")

    if not security.verify_password(
        password_data.current_password, current_user.hashed_password
    ):
        logger.warning(f"Invalid current password for user: {current_user.email}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid current password"
        )

    current_user.hashed_password = security.get_password_hash(
        password_data.new_password
    )
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


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


@router.post("/forgot-password")
async def forgot_password(
    request: ForgotPasswordRequest,
    db: AsyncSession = Depends(deps.get_db),
    background_tasks: BackgroundTasks = BackgroundTasks(),
) -> Any:
    """Send password reset email."""
    logger.info(f"Password reset requested for: {request.email}")

    # Find user by email
    query = select(User).where(User.email == request.email)
    result = await db.execute(query)
    user = result.scalar_one_or_none()

    if user:
        # Generate reset token
        token = "".join(
            secrets.choice(string.ascii_letters + string.digits) for _ in range(32)
        )

        # Store token with expiration (30 minutes)
        password_reset_tokens[token] = {
            "user_id": user.id,
            "email": user.email,
            "expires": datetime.utcnow() + timedelta(minutes=30),
        }

        # In production, send email here
        # background_tasks.add_task(send_reset_email, user.email, token)
        logger.info(f"Reset token generated for user: {user.email}, token: {token}")

    # Always return success to prevent email enumeration
    return {
        "message": (
            "If an account exists with this email, "
            "reset instructions have been sent"
        )
    }


class VerifyResetTokenRequest(BaseModel):
    token: str


@router.post("/verify-reset-token")
async def verify_reset_token(request: VerifyResetTokenRequest) -> Any:
    """Verify if a reset token is valid."""
    token_data = password_reset_tokens.get(request.token)

    if not token_data or token_data["expires"] < datetime.utcnow():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or expired token"
        )

    return {"valid": True}


class ResetPasswordRequest(BaseModel):
    token: str
    password: str


@router.post("/reset-password")
async def reset_password(
    request: ResetPasswordRequest, db: AsyncSession = Depends(deps.get_db)
) -> Any:
    """Reset password using token."""
    token_data = password_reset_tokens.get(request.token)

    if not token_data or token_data["expires"] < datetime.utcnow():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or expired token"
        )

    # Get user
    query = select(User).where(User.id == token_data["user_id"])
    result = await db.execute(query)
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    # Update password
    user.hashed_password = security.get_password_hash(request.password)
    db.add(user)
    await db.commit()

    # Remove used token
    del password_reset_tokens[request.token]

    logger.info(f"Password reset successful for user: {user.email}")
    return {"message": "Password reset successfully"}


@router.post("/logout")
async def logout(current_user: User = Depends(deps.get_current_user)) -> Any:
    """Logout the current user.

    Since JWT tokens are stateless, this endpoint primarily serves to:
    - Confirm logout intent to the client
    - Log the event for audit purposes (when audit logs are implemented)
    - Provide a consistent API interface

    The actual token invalidation should be handled client-side.
    """
    logger.info(f"User logged out: {current_user.email}")

    # TODO: Once audit logs table is implemented, record logout event here
    # await record_audit_log(
    #     user_id=current_user.id,
    #     action="logout",
    #     timestamp=datetime.utcnow()
    # )

    return {"message": "Successfully logged out"}
