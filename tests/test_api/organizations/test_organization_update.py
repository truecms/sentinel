import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.organization import Organization
from app.models.user import User

pytestmark = pytest.mark.asyncio

async def test_update_organization(
    client: AsyncClient,
    superuser_token_headers: dict,
    test_organization: Organization
):
    """Test updating an organization."""
    org_id = test_organization.id
    response = await client.put(
        f"/api/v1/organizations/{org_id}",
        headers=superuser_token_headers,
        json={
            "name": "Updated Organization",
            "is_active": True
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Updated Organization"
    assert data["is_active"] == True

async def test_update_organization_invalid_data(
    client: AsyncClient,
    superuser_token_headers: dict,
    test_organization: Organization
):
    """Test updating an organization with invalid data."""
    org_id = test_organization.id
    response = await client.put(
        f"/api/v1/organizations/{org_id}",
        headers=superuser_token_headers,
        json={
            "name": "",  # Empty name should be invalid
            "is_active": "invalid_boolean"  # Invalid boolean value
        }
    )
    assert response.status_code == 422

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
            "is_active": True
        }
    )
    assert response.status_code == 403

async def test_update_organization_success(
    client: AsyncClient,
    superuser_token_headers: dict,
    test_organization: Organization,
    db_session: AsyncSession
):
    """Test successful organization update with all fields."""
    response = await client.put(
        f"/api/v1/organizations/{test_organization.id}",
        headers=superuser_token_headers,
        json={
            "name": "Updated Organization",
            "description": "Updated Description",
            "is_active": True
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Updated Organization"
    assert data["description"] == "Updated Description"
    assert data["is_active"] == True

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

async def test_update_organization_with_users(
    client: AsyncClient,
    superuser_token_headers: dict,
    test_organization: Organization,
    test_user: User,
    db_session: AsyncSession
):
    """Test updating organization with user associations."""
    response = await client.put(
        f"/api/v1/organizations/{test_organization.id}",
        headers=superuser_token_headers,
        json={
            "name": "Updated Organization",
            "description": "Updated Description",
            "user_ids": [test_user.id]
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Updated Organization"
    assert data["description"] == "Updated Description" 