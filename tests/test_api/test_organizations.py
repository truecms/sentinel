import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.organization import Organization
from app.models.user import User
from app.core.security import get_password_hash
from app.db.session import async_session_maker

pytestmark = pytest.mark.asyncio

async def test_create_organization(
    client: AsyncClient,
    superuser_token_headers: dict,
    test_user: User
):
    """Test creating a new organization."""
    test_user_id = test_user.id  # Store ID before async operation
    response = await client.post(
        "/api/v1/organizations/",
        headers=superuser_token_headers,
        json={
            "name": "New Organization",
            "created_by": test_user_id
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "New Organization"
    assert "id" in data
    assert data["created_by"] == test_user_id

async def test_create_organization_duplicate_name(
    client: AsyncClient,
    superuser_token_headers: dict,  # Use superuser token instead of user token
    test_organization: Organization
):
    """Test creating organization with duplicate name."""
    org_name = test_organization.name  # Store name before async operation
    response = await client.post(
        "/api/v1/organizations/",
        headers=superuser_token_headers,
        json={
            "name": org_name,
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
    org_id = test_organization.id  # Store ID before async operation
    org_name = test_organization.name  # Store name before async operation
    response = await client.get(
        f"/api/v1/organizations/{org_id}",
        headers=superuser_token_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == org_id
    assert data["name"] == org_name

async def test_get_organizations(
    client: AsyncClient,
    superuser_token_headers: dict,
    test_organization: Organization
):
    """Test getting list of organizations."""
    org_id = test_organization.id  # Store ID before async operation
    response = await client.get(
        "/api/v1/organizations/",
        headers=superuser_token_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    assert any(org["id"] == org_id for org in data)

async def test_update_organization(
    client: AsyncClient,
    superuser_token_headers: dict,
    test_organization: Organization
):
    """Test updating an organization."""
    org_id = test_organization.id  # Store ID before async operation
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

async def test_delete_organization(
    client: AsyncClient,
    superuser_token_headers: dict,
    test_organization: Organization
):
    """Test deleting an organization."""
    org_id = test_organization.id  # Store ID before async operation
    response = await client.delete(
        f"/api/v1/organizations/{org_id}",
        headers=superuser_token_headers
    )
    assert response.status_code == 200
    
    # Verify organization is deleted
    response = await client.get(
        f"/api/v1/organizations/{org_id}",
        headers=superuser_token_headers
    )
    assert response.status_code == 404

async def test_delete_organization_regular_user(
    client: AsyncClient,
    user_token_headers: dict,
    test_organization: Organization
):
    """Test that regular users cannot delete organizations."""
    org_id = test_organization.id  # Store ID before async operation
    response = await client.delete(
        f"/api/v1/organizations/{org_id}",
        headers=user_token_headers
    )
    assert response.status_code == 403

async def test_get_organization_unauthorized(
    client: AsyncClient,
    test_organization: Organization
):
    """Test accessing organization without authentication."""
    org_id = test_organization.id  # Store ID before async operation
    response = await client.get(
        f"/api/v1/organizations/{org_id}"
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
    # Store IDs before async operations
    org_id = test_organization.id
    superuser_id = test_superuser.id

    # Create an organization admin user
    org_admin = User(
        email="orgadmin@example.com",
        hashed_password=get_password_hash("testpass123"),
        organization_id=org_id,
        role="organization_admin",
        is_active=True
    )
    db_session.add(org_admin)
    await db_session.commit()
    await db_session.refresh(org_admin)

    # Create another organization that shouldn't be visible
    other_org = Organization(
        name="Other Organization",
        created_by=superuser_id,
        updated_by=superuser_id
    )
    db_session.add(other_org)
    await db_session.commit()
    await db_session.refresh(other_org)
    other_org_id = other_org.id

    # Get token for org admin
    response = await client.post(
        "/api/v1/auth/access-token",
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
    assert data[0]["id"] == org_id
    assert not any(org["id"] == other_org_id for org in data)

async def test_create_organization_invalid_data(
    client: AsyncClient,
    superuser_token_headers: dict
):
    """Test creating an organization with invalid data."""
    response = await client.post(
        "/api/v1/organizations/",
        headers=superuser_token_headers,
        json={
            "name": "",  # Empty name should be invalid
            "description": "Test description"
        }
    )
    assert response.status_code == 422

async def test_update_organization_invalid_data(
    client: AsyncClient,
    superuser_token_headers: dict,
    test_organization: Organization
):
    """Test updating an organization with invalid data."""
    org_id = test_organization.id  # Store ID before async operation
    response = await client.put(
        f"/api/v1/organizations/{org_id}",
        headers=superuser_token_headers,
        json={
            "name": "",  # Empty name should be invalid
            "is_active": "invalid_boolean"  # Invalid boolean value
        }
    )
    assert response.status_code == 422

async def test_list_organizations_with_filters(
    client: AsyncClient,
    superuser_token_headers: dict,
    test_organization: Organization,
    db_session: AsyncSession
):
    """Test listing organizations with filters."""
    # Store organization name and ID before async operation
    org_name = test_organization.name
    org_id = test_organization.id
    creator_id = test_organization.created_by

    # Create another organization with different status
    inactive_org = Organization(
        name="Inactive Organization",
        is_active=False,
        created_by=creator_id
    )
    db_session.add(inactive_org)
    await db_session.commit()

    # Test filtering by active status
    response = await client.get(
        "/api/v1/organizations/?is_active=true",
        headers=superuser_token_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert all(org["is_active"] for org in data)

    # Test filtering by name
    response = await client.get(
        f"/api/v1/organizations/?name={org_name}",
        headers=superuser_token_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert all(org["name"] == org_name for org in data)

async def test_delete_organization_with_resources(
    client: AsyncClient,
    superuser_token_headers: dict,
    test_organization: Organization,
    db_session: AsyncSession
):
    """Test deleting an organization that has associated resources."""
    org_id = test_organization.id  # Store ID before async operation
    
    # Add a user to the organization
    from app.models.user import User
    from app.core.security import get_password_hash
    
    org_user = User(
        email="org_user@example.com",
        hashed_password=get_password_hash("testpass123"),
        organization_id=org_id,
        is_active=True
    )
    db_session.add(org_user)
    await db_session.commit()
    
    # Delete the organization
    response = await client.delete(
        f"/api/v1/organizations/{org_id}",
        headers=superuser_token_headers
    )
    assert response.status_code == 200
    
    # Verify the organization is marked as deleted
    response = await client.get(
        f"/api/v1/organizations/{org_id}",
        headers=superuser_token_headers
    )
    assert response.status_code == 404
    
    # Verify associated user's organization_id is set to None
    from sqlalchemy import select
    user_query = select(User).where(User.email == "org_user@example.com")
    result = await db_session.execute(user_query)
    user = result.scalar_one()
    assert user.organization_id is None

async def test_update_organization_success(client: AsyncClient, test_organization: Organization, test_superuser: User, superuser_token_headers: dict):
    """Test successful organization update."""
    update_data = {
        "name": "Updated Organization",
        "description": "Updated description",
        "is_active": True
    }
    response = await client.put(
        f"/api/v1/organizations/{test_organization.id}",
        json=update_data,
        headers=superuser_token_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == update_data["name"]
    assert data["description"] == update_data["description"]
    assert data["is_active"] == update_data["is_active"]

async def test_list_organizations_pagination(client: AsyncClient, test_superuser: User, superuser_token_headers: dict):
    """Test organization listing with pagination."""
    # Create multiple organizations
    org_names = ["Org 1", "Org 2", "Org 3"]
    for name in org_names:
        await client.post(
            "/api/v1/organizations/",
            json={"name": name},
            headers=superuser_token_headers
        )
    
    # Test pagination
    response = await client.get(
        "/api/v1/organizations/?skip=1&limit=2",
        headers=superuser_token_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) <= 2  # Should respect the limit

async def test_delete_organization_cascade(
    client: AsyncClient,
    test_organization: Organization,
    test_superuser: User,
    superuser_token_headers: dict,
    db_session: AsyncSession
):
    """Test organization deletion with cascade effect on related entities."""
    # Store organization ID before async operations
    org_id = test_organization.id

    # Create a user associated with the organization
    user_data = {
        "email": "test_cascade@example.com",
        "password": "testpassword123",
        "organization_id": org_id,
        "role": "user",
        "is_active": True,
        "is_superuser": False
    }

    # Create user
    user_response = await client.post(
        "/api/v1/users/",
        json=user_data,
        headers=superuser_token_headers
    )
    assert user_response.status_code == 200

    # Delete the organization
    response = await client.delete(
        f"/api/v1/organizations/{org_id}",
        headers=superuser_token_headers
    )
    assert response.status_code == 200

    # Verify organization is marked as deleted and user's organization_id is set to None
    async with async_session_maker() as session:
        async with session.begin():
            # Check organization status
            org_query = select(Organization).where(Organization.id == org_id)
            result = await session.execute(org_query)
            deleted_org = result.scalar_one()
            assert deleted_org.is_deleted is True
            assert deleted_org.is_active is False

            # Check user's organization_id
            user_query = select(User).where(User.email == "test_cascade@example.com")
            result = await session.execute(user_query)
            user = result.scalar_one()
            assert user.organization_id is None

async def test_update_organization_not_found(client: AsyncClient, test_superuser: User, superuser_token_headers: dict):
    """Test updating a non-existent organization."""
    update_data = {
        "name": "Updated Organization",
        "description": "Updated description"
    }
    response = await client.put(
        "/api/v1/organizations/99999",
        json=update_data,
        headers=superuser_token_headers
    )
    assert response.status_code == 404
