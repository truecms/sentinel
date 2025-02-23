import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.organization import Organization
from app.models.user import User

pytestmark = pytest.mark.asyncio

async def test_create_organization_non_superuser(
    client: AsyncClient,
    db_session: AsyncSession,
    regular_user_token_headers: dict
):
    """Test that non-superuser cannot create organization."""
    response = await client.post(
        "/api/v1/organizations/",
        headers=regular_user_token_headers,
        json={
            "name": "Test Organization",
            "description": "Test Description"
        }
    )
    assert response.status_code == 403

async def test_read_organization_unauthorized_access(
    client: AsyncClient,
    db_session: AsyncSession,
    regular_user_token_headers: dict,
    test_organization: Organization
):
    """Test unauthorized access to organization details."""
    response = await client.get(
        f"/api/v1/organizations/{test_organization.id}",
        headers=regular_user_token_headers
    )
    assert response.status_code == 403

async def test_update_organization_non_superuser(
    client: AsyncClient,
    db_session: AsyncSession,
    regular_user_token_headers: dict,
    test_organization: Organization
):
    """Test that non-superuser cannot update organization."""
    response = await client.put(
        f"/api/v1/organizations/{test_organization.id}",
        headers=regular_user_token_headers,
        json={
            "name": "Updated Organization",
            "description": "Updated Description"
        }
    )
    assert response.status_code == 403

async def test_delete_organization_non_superuser(
    client: AsyncClient,
    db_session: AsyncSession,
    regular_user_token_headers: dict,
    test_organization: Organization
):
    """Test that non-superuser cannot delete organization."""
    response = await client.delete(
        f"/api/v1/organizations/{test_organization.id}",
        headers=regular_user_token_headers
    )
    assert response.status_code == 403

async def test_read_organizations_superuser(
    client: AsyncClient,
    superuser_token_headers: dict,
    test_organization: Organization
):
    """Test reading organizations as superuser."""
    response = await client.get(
        "/api/v1/organizations/",
        headers=superuser_token_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    assert any(org["id"] == test_organization.id for org in data)

async def test_read_organizations_regular_user(
    client: AsyncClient,
    user_token_headers: dict,
    test_organization: Organization,
    test_user: User
):
    """Test reading organizations as regular user."""
    response = await client.get(
        "/api/v1/organizations/",
        headers=user_token_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    # Regular user should only see their organization
    assert all(org["id"] == test_user.organization_id for org in data)

async def test_read_organization_unauthorized(
    client: AsyncClient,
    user_token_headers: dict,
    test_organization: Organization
):
    """Test reading organization without proper authorization."""
    response = await client.get(
        f"/api/v1/organizations/{test_organization.id}",
        headers=user_token_headers
    )
    assert response.status_code == 403

async def test_update_organization_regular_user(
    client: AsyncClient,
    user_token_headers: dict,
    test_organization: Organization
):
    """Test updating organization as regular user."""
    response = await client.put(
        f"/api/v1/organizations/{test_organization.id}",
        headers=user_token_headers,
        json={
            "name": "Updated Organization",
            "description": "Updated Description"
        }
    )
    assert response.status_code == 403

async def test_delete_organization_regular_user(
    client: AsyncClient,
    user_token_headers: dict,
    test_organization: Organization
):
    """Test deleting organization as regular user."""
    response = await client.delete(
        f"/api/v1/organizations/{test_organization.id}",
        headers=user_token_headers
    )
    assert response.status_code == 403 