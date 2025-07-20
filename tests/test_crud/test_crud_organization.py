"""Tests for organization CRUD operations."""

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud import crud_organization
from app.models.organization import Organization
from app.schemas.organization import OrganizationCreate, OrganizationUpdate


class TestOrganizationCRUD:
    """Test cases for Organization CRUD operations."""

    @pytest.fixture
    async def test_organization(self, db_session: AsyncSession, test_user):
        """Create a test organization for use in tests."""
        org = Organization(
            name="Test Organization",
            description="Test organization for testing",
            is_active=True,
            created_by=test_user.id,
            updated_by=test_user.id,
        )
        db_session.add(org)
        await db_session.commit()
        await db_session.refresh(org)
        return org

    async def test_get_organization(self, db_session: AsyncSession, test_organization):
        """Test getting an organization by ID."""
        org = await crud_organization.get_organization(db_session, organization_id=test_organization.id)
        assert org is not None
        assert org.id == test_organization.id
        assert org.name == "Test Organization"

    async def test_get_organization_not_found(self, db_session: AsyncSession):
        """Test getting a non-existent organization."""
        org = await crud_organization.get_organization(db_session, organization_id=999999)
        assert org is None

    async def test_create_organization(self, db_session: AsyncSession, test_user):
        """Test creating a new organization."""
        org_data = OrganizationCreate(
            name="New Organization",
            description="A new organization",
        )
        
        org = await crud_organization.create_organization(
            db_session, organization=org_data, created_by=test_user.id
        )
        
        assert org.id is not None
        assert org.name == "New Organization"
        assert org.description == "A new organization"
        assert org.created_by == test_user.id