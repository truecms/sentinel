import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.organization import Organization
from app.models.user import User

_ = pytest.mark.asyncio


async def test_get_organization(
    client: AsyncClient, superuser_token_headers: dict, test_organization: Organization
):
    """Test getting a specific organization."""
    org_id = test_organization.id
    org_name = test_organization.name
    response = await client.get(
        f"/api/v1/organizations/{org_id}", headers=superuser_token_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == org_id
    assert data["name"] == org_name


async def test_get_organizations(
    client: AsyncClient, superuser_token_headers: dict, test_organization: Organization
):
    """Test getting list of organizations."""
    org_id = test_organization.id
    response = await client.get(
        "/api/v1/organizations/", headers=superuser_token_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    assert any(org["id"] == org_id for org in data)


async def test_get_organization_unauthorized(
    client: AsyncClient, test_organization: Organization
):
    """Test accessing organization without authentication."""
    org_id = test_organization.id
    response = await client.get(f"/api/v1/organizations/{org_id}")
    assert response.status_code == 401


async def test_get_nonexistent_organization(
    client: AsyncClient, user_token_headers: dict
):
    """Test getting non-existent organization."""
    response = await client.get(
        "/api/v1/organizations/99999", headers=user_token_headers
    )
    assert response.status_code == 404


async def test_read_organization_unauthorized_access(
    client: AsyncClient,
    db_session: AsyncSession,
    regular_user_token_headers: dict,
    test_organization: Organization,
):
    """Test unauthorized access to organization details."""
    response = await client.get(
        f"/api/v1/organizations/{test_organization.id}",
        headers=regular_user_token_headers,
    )
    assert response.status_code == 403


async def test_read_organizations_superuser(
    client: AsyncClient,
    superuser_token_headers: dict,
    test_organization: Organization,
    db_session: AsyncSession,
):
    """Test reading organizations as superuser."""
    org_id = test_organization.id
    response = await client.get(
        "/api/v1/organizations/", headers=superuser_token_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    assert any(org["id"] == org_id for org in data)


async def test_read_organizations_regular_user(
    client: AsyncClient,
    user_token_headers: dict,
    test_organization: Organization,
    test_user: User,
):
    """Test reading organizations as regular user."""
    response = await client.get("/api/v1/organizations/", headers=user_token_headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    # Regular user should only see their organization
    assert all(org["id"] == test_user.organization_id for org in data)


async def test_read_organization(
    client: AsyncClient,
    superuser_token_headers: dict,
    test_organization: Organization,
    db_session: AsyncSession,
):
    """Test reading specific organization details."""
    org_id = test_organization.id
    org_name = test_organization.name
    response = await client.get(
        f"/api/v1/organizations/{org_id}", headers=superuser_token_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == org_id
    assert data["name"] == org_name


async def test_read_organization_not_found(
    client: AsyncClient, superuser_token_headers: dict
):
    """Test reading non-existent organization."""
    response = await client.get(
        "/api/v1/organizations/99999", headers=superuser_token_headers
    )
    assert response.status_code == 404


async def test_read_organization_unauthorized(
    client: AsyncClient, user_token_headers: dict, test_organization: Organization
):
    """Test reading organization without proper authorization."""
    response = await client.get(
        f"/api/v1/organizations/{test_organization.id}", headers=user_token_headers
    )
    assert response.status_code == 403
