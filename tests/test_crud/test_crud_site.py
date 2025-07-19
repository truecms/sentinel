"""Tests for site CRUD operations."""

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud import crud_site
from app.models.site import Site
from app.schemas.site import SiteCreate


class TestSiteCRUD:
    """Test cases for Site CRUD operations."""

    @pytest.fixture
    async def test_site(self, db_session: AsyncSession, test_user, test_organization):
        """Create a test site for use in tests."""
        site = Site(
            url="https://test-site.example.com",
            name="Test Site",
            organization_id=test_organization.id,
            uuid="test-site-uuid-123",
            api_token="test-api-token",
            is_active=True,
            created_by=test_user.id,
            updated_by=test_user.id,
        )
        db_session.add(site)
        await db_session.commit()
        await db_session.refresh(site)
        return site

    async def test_get_site(self, db_session: AsyncSession, test_site):
        """Test getting a site by ID."""
        site = await crud_site.get_site(db_session, site_id=test_site.id)
        assert site is not None
        assert site.id == test_site.id
        assert site.name == "Test Site"