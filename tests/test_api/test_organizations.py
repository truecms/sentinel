import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.organization import Organization
from app.models.user import User
from app.core.security import get_password_hash

pytestmark = pytest.mark.asyncio

async def test_create_organization(
    client: AsyncClient,
    superuser_token_headers: dict,
    test_user: User
):
    """Test creating a new organization."""
    response = await client.post(
        "/api/v1/organizations/",
        headers=superuser_token_headers,
        json={
            "name": "New Organization",
            "created_by": test_user.id
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "New Organization"
    assert "id" in data
    assert data["created_by"] == test_user.id

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
    superuser_token_headers: dict,
    test_organization: Organization
):
    """Test getting a specific organization."""
    response = await client.get(
        f"/api/v1/organizations/{test_organization.id}",
        headers=superuser_token_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == test_organization.id
    assert data["name"] == test_organization.name

async def test_get_organizations(
    client: AsyncClient,
    superuser_token_headers: dict,
    test_organization: Organization
):
    """Test getting list of organizations."""
    response = await client.get(
        "/api/v1/organizations/",
        headers=superuser_token_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    assert any(org["id"] == test_organization.id for org in data)

async def test_update_organization(
    client: AsyncClient,
    superuser_token_headers: dict,
    test_organization: Organization
):
    """Test updating an organization."""
    response = await client.put(
        f"/api/v1/organizations/{test_organization.id}",
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

async def test_delete_organization(
    client: AsyncClient,
    superuser_token_headers: dict,
    test_organization: Organization
):
    """Test deleting an organization."""
    response = await client.delete(
        f"/api/v1/organizations/{test_organization.id}",
        headers=superuser_token_headers
    )
    assert response.status_code == 200
    
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

async def test_get_organizations_as_org_admin(
    client: AsyncClient,
    db_session: AsyncSession,
    test_organization: Organization,
    test_superuser: User
):
    """Test that organization admin can only see their own organization."""
    # Create an organization admin user
    org_admin = User(
        email="orgadmin@example.com",
        hashed_password=get_password_hash("testpass123"),
        organization_id=test_organization.id,
        role="organization_admin",
        is_active=True
    )
    db_session.add(org_admin)
    await db_session.commit()
    await db_session.refresh(org_admin)

    # Create another organization that shouldn't be visible
    other_org = Organization(
        name="Other Organization",
        created_by=test_superuser.id,
        updated_by=test_superuser.id
    )
    db_session.add(other_org)
    await db_session.commit()
    await db_session.refresh(other_org)

    # Get token for org admin
    response = await client.post(
        "/api/v1/auth/login",
        data={
            "username": org_admin.email,
            "password": "testpass123"
        }
    )
    assert response.status_code == 200
    token = response.json()["access_token"]

    # Test organization listing
    response = await client.get(
        "/api/v1/organizations/",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 1
    assert data[0]["id"] == test_organization.id
    assert not any(org["id"] == other_org.id for org in data)
