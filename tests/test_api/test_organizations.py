import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.organization import Organization
from app.models.user import User

pytestmark = pytest.mark.asyncio

async def test_create_organization(
    client: AsyncClient,
    user_token_headers: dict
):
    """Test creating a new organization."""
    response = await client.post(
        "/api/v1/organizations/",
        headers=user_token_headers,
        json={
            "name": "New Test Organization",
            "tax_id": "123456789"
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "New Test Organization"
    assert "id" in data
    assert "created_at" in data

async def test_create_organization_duplicate_name(
    client: AsyncClient,
    user_token_headers: dict,
    test_organization: Organization
):
    """Test creating organization with duplicate name."""
    response = await client.post(
        "/api/v1/organizations/",
        headers=user_token_headers,
        json={
            "name": test_organization.name,
            "tax_id": "987654321"
        }
    )
    assert response.status_code == 409

async def test_get_organization(
    client: AsyncClient,
    user_token_headers: dict,
    test_organization: Organization
):
    """Test getting organization details."""
    response = await client.get(
        f"/api/v1/organizations/{test_organization.id}",
        headers=user_token_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == test_organization.name
    assert data["id"] == test_organization.id

async def test_get_organizations(
    client: AsyncClient,
    user_token_headers: dict,
    test_organization: Organization
):
    """Test getting list of organizations."""
    response = await client.get(
        "/api/v1/organizations/",
        headers=user_token_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert any(org["id"] == test_organization.id for org in data)

async def test_update_organization(
    client: AsyncClient,
    user_token_headers: dict,
    test_organization: Organization
):
    """Test updating organization details."""
    response = await client.put(
        f"/api/v1/organizations/{test_organization.id}",
        headers=user_token_headers,
        json={
            "name": "Updated Organization Name",
            "tax_id": "987654321"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Updated Organization Name"
    assert data["id"] == test_organization.id

async def test_delete_organization(
    client: AsyncClient,
    superuser_token_headers: dict,
    test_organization: Organization
):
    """Test deleting an organization (superuser only)."""
    response = await client.delete(
        f"/api/v1/organizations/{test_organization.id}",
        headers=superuser_token_headers
    )
    assert response.status_code == 204

    # Verify organization is deleted
    response = await client.get(
        f"/api/v1/organizations/{test_organization.id}",
        headers=superuser_token_headers
    )
    assert response.status_code == 404

async def test_delete_organization_regular_user(
    client: AsyncClient,
    user_token_headers: dict,
    test_organization: Organization
):
    """Test that regular users cannot delete organizations."""
    response = await client.delete(
        f"/api/v1/organizations/{test_organization.id}",
        headers=user_token_headers
    )
    assert response.status_code == 403

async def test_get_organization_unauthorized(
    client: AsyncClient,
    test_organization: Organization
):
    """Test accessing organization without authentication."""
    response = await client.get(
        f"/api/v1/organizations/{test_organization.id}"
    )
    assert response.status_code == 401

async def test_get_nonexistent_organization(
    client: AsyncClient,
    user_token_headers: dict
):
    """Test getting non-existent organization."""
    response = await client.get(
        "/api/v1/organizations/99999",
        headers=user_token_headers
    )
    assert response.status_code == 404
