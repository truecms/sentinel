import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_password_hash
from app.models.organization import Organization
from app.models.user import User

pytestmark = pytest.mark.asyncio


async def test_get_organizations_as_org_admin(
    client: AsyncClient,
    db_session: AsyncSession,
    test_organization: Organization,
    test_superuser: User,
):
    """Test that organization admin can only see their own organization."""
    # Store IDs before async operations
    org_id = test_organization.id
    superuser_id = test_superuser.id

    # Create an organization admin user (without setting organization_id initially to avoid FK constraint)
    org_admin = User(
        email="orgadmin@example.com",
        hashed_password=get_password_hash("testpass123"),
        role="organization_admin",
        is_active=True,
    )
    db_session.add(org_admin)
    await db_session.commit()
    await db_session.refresh(org_admin)
    
    # Now set the organization_id after user is created
    org_admin.organization_id = org_id
    db_session.add(org_admin)
    await db_session.commit()

    # Add user to organization junction table
    from app.models.user_organization import user_organization
    await db_session.execute(
        user_organization.insert().values(
            user_id=org_admin.id, organization_id=org_id
        )
    )
    await db_session.commit()

    # Create another organization that shouldn't be visible
    other_org = Organization(
        name="Other Organization", created_by=superuser_id, updated_by=superuser_id
    )
    db_session.add(other_org)
    await db_session.commit()
    await db_session.refresh(other_org)
    other_org_id = other_org.id

    # Get token for org admin
    response = await client.post(
        "/api/v1/auth/access-token",
        data={"username": org_admin.email, "password": "testpass123"},
    )
    assert response.status_code == 200
    token = response.json()["access_token"]

    # Test organization listing
    response = await client.get(
        "/api/v1/organizations/", headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 1
    assert data[0]["id"] == org_id
    assert not any(org["id"] == other_org_id for org in data)


async def test_list_organizations_regular_user(
    client: AsyncClient,
    regular_user_token_headers: dict,
    test_organization: Organization,
    test_regular_user: User,
    db_session: AsyncSession,
):
    """Test listing organizations as regular user."""
    # Assign test_regular_user to test_organization
    test_regular_user.organization_id = test_organization.id
    db_session.add(test_regular_user)
    await db_session.commit()
    
    # Add user to organization junction table
    from app.models.user_organization import user_organization
    await db_session.execute(
        user_organization.insert().values(
            user_id=test_regular_user.id, organization_id=test_organization.id
        )
    )
    await db_session.commit()
    
    # Create another organization
    other_org = Organization(
        name="Other Organization",
        created_by=test_regular_user.id,
        updated_by=test_regular_user.id,
    )
    db_session.add(other_org)
    await db_session.commit()

    response = await client.get(
        "/api/v1/organizations/", headers=regular_user_token_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    # Regular user should only see their organization
    assert len(data) == 1
    assert data[0]["id"] == test_regular_user.organization_id


async def test_create_organization_with_users(
    client: AsyncClient,
    superuser_token_headers: dict,
    test_user: User,
    db_session: AsyncSession,
):
    """Test creating organization with associated users."""
    response = await client.post(
        "/api/v1/organizations/",
        headers=superuser_token_headers,
        json={
            "name": "Test Organization",
            "description": "Test Description",
            "users": [test_user.id],
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Test Organization"
    assert "id" in data

    # Verify user association
    await db_session.refresh(test_user)
    assert test_user.organization_id == data["id"]


async def test_update_organization_with_users(
    client: AsyncClient,
    superuser_token_headers: dict,
    test_organization: Organization,
    test_user: User,
    db_session: AsyncSession,
):
    """Test updating organization with user associations."""
    response = await client.put(
        f"/api/v1/organizations/{test_organization.id}",
        headers=superuser_token_headers,
        json={
            "name": "Updated Organization",
            "description": "Updated Description",
            "users": [test_user.id],
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Updated Organization"

    # Verify user association
    await db_session.refresh(test_user)
    assert test_user.organization_id == test_organization.id
