"""
Fixtures specific to organization tests.
"""

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.organization import Organization
from app.models.user import User


@pytest.fixture
async def test_organization(db_session: AsyncSession, test_user: User) -> Organization:
    """Create a test organization."""
    organization = Organization(
        name="Test Organization",
        created_by=test_user.id,
        updated_by=test_user.id,
        is_active=True,
        is_deleted=False,
    )
    db_session.add(organization)
    await db_session.commit()
    await db_session.refresh(organization)
    return organization


@pytest.fixture
async def test_inactive_organization(
    db_session: AsyncSession, test_user: User
) -> Organization:
    """Create an inactive test organization."""
    organization = Organization(
        name="Inactive Organization",
        created_by=test_user.id,
        updated_by=test_user.id,
        is_active=False,
        is_deleted=False,
    )
    db_session.add(organization)
    await db_session.commit()
    await db_session.refresh(organization)
    return organization


@pytest.fixture
async def test_deleted_organization(
    db_session: AsyncSession, test_user: User
) -> Organization:
    """Create a deleted test organization."""
    organization = Organization(
        name="Deleted Organization",
        created_by=test_user.id,
        updated_by=test_user.id,
        is_active=True,
        is_deleted=True,
    )
    db_session.add(organization)
    await db_session.commit()
    await db_session.refresh(organization)
    return organization
