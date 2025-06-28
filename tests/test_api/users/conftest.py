"""
Fixtures specific to user tests.
"""

import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User
from app.models.organization import Organization
from app.core.security import get_password_hash

@pytest.fixture
async def test_user(
    db_session: AsyncSession
) -> User:
    """Create a test user."""
    # Create base organization first
    org = Organization(
        name="Test Organization"
    )
    db_session.add(org)
    await db_session.commit()
    await db_session.refresh(org)

    # Create user
    user = User(
        email="test_user@example.com",
        hashed_password=get_password_hash("testpass123"),
        is_active=True,
        is_superuser=False,
        role="user",
        organization_id=org.id
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    # Update organization with created_by
    org.created_by = user.id
    await db_session.commit()
    
    return user

@pytest.fixture
async def test_inactive_user(
    db_session: AsyncSession,
    test_organization: Organization
) -> User:
    """Create an inactive test user."""
    user = User(
        email="inactive_user@example.com",
        hashed_password=get_password_hash("testpass123"),
        is_active=False,
        is_superuser=False,
        role="user",
        organization_id=test_organization.id
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user

@pytest.fixture
async def test_admin_user(
    db_session: AsyncSession,
    test_organization: Organization
) -> User:
    """Create an admin test user."""
    user = User(
        email="admin_user@example.com",
        hashed_password=get_password_hash("testpass123"),
        is_active=True,
        is_superuser=False,
        role="admin",
        organization_id=test_organization.id
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user

@pytest.fixture
async def test_superuser(
    db_session: AsyncSession,
    test_organization: Organization
) -> User:
    """Create a superuser."""
    user = User(
        email="superuser@example.com",
        hashed_password=get_password_hash("testpass123"),
        is_active=True,
        is_superuser=True,
        role="admin",
        organization_id=test_organization.id
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user 