"""
Fixtures specific to site tests.
"""

import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.site import Site
from app.models.organization import Organization
from app.models.user import User

@pytest.fixture
async def test_site(
    db_session: AsyncSession,
    test_organization: Organization,
    test_user: User
) -> Site:
    """Create a test site."""
    site = Site(
        name="Test Site",
        url="https://test.example.com",
        description="Test site description",
        organization_id=test_organization.id,
        created_by=test_user.id,
        updated_by=test_user.id,
        is_active=True,
        is_deleted=False
    )
    db_session.add(site)
    await db_session.commit()
    await db_session.refresh(site)
    return site

@pytest.fixture
async def test_inactive_site(
    db_session: AsyncSession,
    test_organization: Organization,
    test_user: User
) -> Site:
    """Create an inactive test site."""
    site = Site(
        name="Inactive Site",
        url="https://inactive.example.com",
        description="Inactive test site",
        organization_id=test_organization.id,
        created_by=test_user.id,
        updated_by=test_user.id,
        is_active=False,
        is_deleted=False
    )
    db_session.add(site)
    await db_session.commit()
    await db_session.refresh(site)
    return site

@pytest.fixture
async def test_deleted_site(
    db_session: AsyncSession,
    test_organization: Organization,
    test_user: User
) -> Site:
    """Create a deleted test site."""
    site = Site(
        name="Deleted Site",
        url="https://deleted.example.com",
        description="Deleted test site",
        organization_id=test_organization.id,
        created_by=test_user.id,
        updated_by=test_user.id,
        is_active=True,
        is_deleted=True
    )
    db_session.add(site)
    await db_session.commit()
    await db_session.refresh(site)
    return site

@pytest.fixture
async def test_monitored_site(
    db_session: AsyncSession,
    test_organization: Organization,
    test_user: User
) -> Site:
    """Create a test site with monitoring data."""
    site = Site(
        name="Monitored Site",
        url="https://monitored.example.com",
        description="Site with monitoring data",
        organization_id=test_organization.id,
        created_by=test_user.id,
        updated_by=test_user.id,
        is_active=True,
        is_deleted=False,
        last_check_time="2024-02-23T00:00:00Z",
        status="up",
        response_time=150,  # milliseconds
        ssl_expiry="2025-02-23T00:00:00Z"
    )
    db_session.add(site)
    await db_session.commit()
    await db_session.refresh(site)
    return site 