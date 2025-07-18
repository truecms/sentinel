from typing import Any, List

from fastapi import APIRouter, Body, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api import deps
from app.core.security import get_password_hash, verify_password
from app.models.organization import Organization
from app.models.user import User
from app.models.user_organization import user_organization

router = APIRouter()


# Add new schema for user me update
class UserMeUpdate(BaseModel):
    email: str | None = None


@router.get("/", response_model=List[UserResponse])
async def read_users(
    db: AsyncSession = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: UserResponse = Depends(deps.get_current_user),
) -> Any:
    """Retrieve users."""
    query = select(User).offset(skip).limit(limit)
    result = await db.execute(query)
    users = result.scalars().all()
    return users


@router.post("/", response_model=UserResponse)
async def create_user(
    *,
    db: AsyncSession = Depends(deps.get_db),
    user_in: UserCreate,
    current_user: UserResponse = Depends(deps.get_current_user),
) -> Any:
    """Create new user."""
    # Check if user has permission
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )

    # Check if user exists
    query = select(User).where(User.email == user_in.email)
    result = await db.execute(query)
    user = result.scalar_one_or_none()

    if user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The user with this email already exists in the system.",
        )

    # Check if organization exists
    query = select(Organization).where(Organization.id == user_in.organization_id)
    result = await db.execute(query)
    organization = result.scalar_one_or_none()

    if not organization:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found",
        )

    # Create user
    user = User(
        email=user_in.email,
        hashed_password=get_password_hash(user_in.password),
        is_superuser=user_in.is_superuser,
        organization_id=user_in.organization_id,
        role=user_in.role,
        is_active=user_in.is_active,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)

    # Add user-organization association
    await db.execute(
        user_organization.insert().values(
            user_id=user.id, organization_id=user_in.organization_id
        )
    )
    await db.commit()

    return user


@router.put("/me", response_model=UserResponse)
async def update_user_me(
    *,
    db: AsyncSession = Depends(deps.get_db),
    user_in: UserMeUpdate,
    current_user: UserResponse = Depends(deps.get_current_user),
) -> Any:
    """Update own user."""
    query = select(User).where(User.id == current_user.id)
    result = await db.execute(query)
    user = result.scalar_one_or_none()

    if user_in.email and user_in.email != user.email:
        # Check if email is already taken
        query = select(User).where(User.email == user_in.email)
        result = await db.execute(query)
        existing_user = result.scalar_one_or_none()
        if existing_user:
            raise HTTPException(status_code=400, detail="Email already registered")
        user.email = user_in.email

    await db.commit()
    await db.refresh(user)
    return user


@router.put("/me/password", response_model=UserResponse)
async def update_user_me_password(
    *,
    db: AsyncSession = Depends(deps.get_db),
    current_password: str = Body(...),
    new_password: str = Body(...),
    current_user: UserResponse = Depends(deps.get_current_user),
) -> Any:
    """Update own password."""
    # Get user from database
    query = select(User).where(User.id == current_user.id)
    result = await db.execute(query)
    user = result.scalar_one_or_none()

    if not verify_password(current_password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Invalid password")

    user.hashed_password = get_password_hash(new_password)
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


@router.get("/me", response_model=UserResponse)
async def read_user_me(
    current_user: UserResponse = Depends(deps.get_current_user),
) -> Any:
    """Get current user."""
    return current_user


@router.get("/{user_id}", response_model=UserResponse)
async def read_user_by_id(
    user_id: int,
    current_user: UserResponse = Depends(deps.get_current_user),
    db: AsyncSession = Depends(deps.get_db),
) -> Any:
    """Get a specific user by id."""
    query = select(User).where(User.id == user_id)
    result = await db.execute(query)
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    return user


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    *,
    db: AsyncSession = Depends(deps.get_db),
    user_id: int,
    user_in: UserUpdate,
    current_user: UserResponse = Depends(deps.get_current_user),
) -> Any:
    """Update a user."""
    # Check if user has permission
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )

    # Get user
    query = select(User).where(User.id == user_id)
    result = await db.execute(query)
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    # Update user fields
    if user_in.email is not None:
        user.email = user_in.email
    if user_in.is_active is not None:
        user.is_active = user_in.is_active
    if user_in.password is not None:
        user.hashed_password = get_password_hash(user_in.password)
    if user_in.role is not None:
        user.role = user_in.role
    if user_in.organization_id is not None:
        # Check if organization exists
        org_query = select(Organization).where(
            Organization.id == user_in.organization_id
        )
        org_result = await db.execute(org_query)
        organization = org_result.scalar_one_or_none()

        if not organization:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Organization not found",
            )

        # Update organization_id and user-organization association
        user.organization_id = user_in.organization_id

        # Remove old association
        await db.execute(
            user_organization.delete().where(user_organization.c.user_id == user.id)
        )

        # Add new association
        await db.execute(
            user_organization.insert().values(
                user_id=user.id, organization_id=user_in.organization_id
            )
        )

    await db.commit()
    await db.refresh(user)
    return user


@router.delete("/{user_id}", response_model=UserResponse)
async def delete_user(
    *,
    db: AsyncSession = Depends(deps.get_db),
    user_id: int,
    current_user: UserResponse = Depends(deps.get_current_user),
) -> Any:
    """Delete a user."""
    # Check if user has permission
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )

    # Get user
    query = select(User).where(User.id == user_id)
    result = await db.execute(query)
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    # Delete user-organization associations first
    await db.execute(
        user_organization.delete().where(user_organization.c.user_id == user.id)
    )

    # Delete user
    await db.delete(user)
    await db.commit()
    return user


@router.get("/organization/{organization_id}/users", response_model=List[UserResponse])
async def get_organization_users(
    *,
    db: AsyncSession = Depends(deps.get_db),
    organization_id: int,
    current_user: UserResponse = Depends(deps.get_current_user),
) -> Any:
    """Get all users in an organization."""
    # Check if organization exists
    query = select(Organization).where(Organization.id == organization_id)
    result = await db.execute(query)
    organization = result.scalar_one_or_none()

    if not organization:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found",
        )

    # Get users through user_organizations table
    query = (
        select(User)
        .join(user_organization)
        .where(user_organization.c.organization_id == organization_id)
    )
    result = await db.execute(query)
    users = result.scalars().all()
    return users
