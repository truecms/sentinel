import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.organization import Organization
from app.models.user import User

_ = pytest.mark.asyncio


async def test_create_organization(
    client: AsyncClient, superuser_token_headers: dict, test_user: User
):
    """Test creating a new organization."""
    test_user_id = test_user.id
    response = await client.post(
        "/api/v1/organizations/",
        headers=superuser_token_headers,
        json={"name": "New Organization", "created_by": test_user_id},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "New Organization"
    assert "id" in data
    assert data["created_by"] == test_user_id


async def test_create_organization_duplicate_name(
    client: AsyncClient,
    superuser_token_headers: dict,
    test_organization: Organization,
    db_session: AsyncSession,
):
    """Test creating organization with duplicate name."""
    org_name = test_organization.name
    response = await client.post(
        "/api/v1/organizations/",
        headers=superuser_token_headers,
        json={"name": org_name, "created_by": test_organization.created_by},
    )
    assert response.status_code == 409
    assert (
        response.json()["detail"] == "The organization with this name already exists."
    )


async def test_create_organization_invalid_data(
    client: AsyncClient, superuser_token_headers: dict
):
    """Test creating an organization with invalid data."""
    response = await client.post(
        "/api/v1/organizations/",
        headers=superuser_token_headers,
        json={
            "name": "",  # Empty name should be invalid
            "description": "Test description",
        },
    )
    assert response.status_code == 422


async def test_create_organization_non_superuser(
    client: AsyncClient, db_session: AsyncSession, regular_user_token_headers: dict
):
    """Test that non-superuser cannot create organization."""
    response = await client.post(
        "/api/v1/organizations/",
        headers=regular_user_token_headers,
        json={"name": "Test Organization", "description": "Test Description"},
    )
    assert response.status_code == 403


async def test_create_organization_empty_name(
    client: AsyncClient, superuser_token_headers: dict
):
    """Test creating organization with empty name."""
    response = await client.post(
        "/api/v1/organizations/",
        headers=superuser_token_headers,
        json={"name": "", "description": "Test Description"},
    )
    assert response.status_code == 422


async def test_create_organization_superuser(
    client: AsyncClient, superuser_token_headers: dict
):
    """Test creating organization as superuser."""
    response = await client.post(
        "/api/v1/organizations/",
        headers=superuser_token_headers,
        json={"name": "Test Organization", "description": "Test Description"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Test Organization"
    assert data["description"] == "Test Description"


async def test_create_organization_regular_user(
    client: AsyncClient, user_token_headers: dict
):
    """Test creating organization as regular user."""
    response = await client.post(
        "/api/v1/organizations/",
        headers=user_token_headers,
        json={"name": "Test Organization", "description": "Test Description"},
    )
    assert response.status_code == 403


async def test_create_organization_with_users(
    client: AsyncClient,
    superuser_token_headers: dict,
    test_user: User,
    db_session: AsyncSession,
):
    """Test creating organization with associated users."""
    response = await client.post(
        "/api/v1/organizations/",
        _=superuser_token_headers,
        json={
            "name": "Test Organization",
            "description": "Test Description",
            "user_ids": [test_user.id],
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Test Organization"
    assert "id" in data
