import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.organization import Organization
from app.models.user import User

pytestmark = pytest.mark.asyncio

async def test_list_organizations_with_filters(
    client: AsyncClient,
    superuser_token_headers: dict,
    test_organization: Organization,
    db_session: AsyncSession
):
    """Test listing organizations with filters."""
    # Create additional organization for testing
    new_org = Organization(
        name="Test Filter Organization",
        description="Test Description",
        created_by=test_organization.created_by,
        updated_by=test_organization.updated_by
    )
    db_session.add(new_org)
    await db_session.commit()

    # Test name filter
    response = await client.get(
        "/api/v1/organizations/",
        headers=superuser_token_headers,
        params={"name": "Filter"}
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["name"] == "Test Filter Organization"

async def test_list_organizations_with_name_filter(
    client: AsyncClient,
    superuser_token_headers: dict,
    test_organization: Organization,
    db_session: AsyncSession
):
    """Test organization listing with name filter."""
    response = await client.get(
        "/api/v1/organizations/",
        headers=superuser_token_headers,
        params={"name": test_organization.name}
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["name"] == test_organization.name

async def test_list_organizations_with_active_filter(
    client: AsyncClient,
    superuser_token_headers: dict,
    test_organization: Organization,
    db_session: AsyncSession,
    test_superuser: User
):
    """Test organization listing with active status filter."""
    # Create inactive organization
    inactive_org = Organization(
        name="Inactive Organization",
        created_by=test_superuser.id,
        updated_by=test_superuser.id,
        is_active=False
    )
    db_session.add(inactive_org)
    await db_session.commit()

    # Test active filter
    response = await client.get(
        "/api/v1/organizations/",
        headers=superuser_token_headers,
        params={"is_active": True}
    )
    assert response.status_code == 200
    data = response.json()
    assert all(org["is_active"] for org in data)

    # Test inactive filter
    response = await client.get(
        "/api/v1/organizations/",
        headers=superuser_token_headers,
        params={"is_active": False}
    )
    assert response.status_code == 200
    data = response.json()
    assert all(not org["is_active"] for org in data)

async def test_list_organizations_pagination(
    client: AsyncClient,
    superuser_token_headers: dict,
    db_session: AsyncSession,
    test_superuser: User
):
    """Test organization listing with pagination."""
    # Create multiple organizations
    for i in range(15):
        org = Organization(
            name=f"Test Organization {i}",
            created_by=test_superuser.id,
            updated_by=test_superuser.id
        )
        db_session.add(org)
    await db_session.commit()

    # Test first page
    response = await client.get(
        "/api/v1/organizations/",
        headers=superuser_token_headers,
        params={"skip": 0, "limit": 10}
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 10

    # Test second page
    response = await client.get(
        "/api/v1/organizations/",
        headers=superuser_token_headers,
        params={"skip": 10, "limit": 10}
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    assert len(data) <= 10 