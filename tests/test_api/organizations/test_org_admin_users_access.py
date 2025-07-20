"""Test org_admin access to organization users endpoint."""
import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_password_hash
from app.models.organization import Organization
from app.models.role import Role, UserRole
from app.models.user import User
from app.models.user_organization import user_organization


@pytest.mark.asyncio
async def test_org_admin_can_view_organization_users(
    client: AsyncClient,
    db_session: AsyncSession,
    test_organization: Organization,
    test_user: User,
):
    """Test that org_admin users can view users in their organization."""
    # Store org ID to avoid async issues
    org_id = test_organization.id
    print(f"\n🔍 Test Organization ID: {org_id}")
    
    # Create org_admin user
    org_admin_user = User(
        email="org.admin@test.com",
        hashed_password=get_password_hash("test123"),
        is_active=True,
        organization_id=org_id,
        role="user"
    )
    db_session.add(org_admin_user)
    await db_session.commit()
    await db_session.refresh(org_admin_user)
    
    # Add org_admin to organization
    await db_session.execute(
        user_organization.insert().values(
            user_id=org_admin_user.id,
            organization_id=org_id
        )
    )
    await db_session.commit()
    
    # Get org_admin role
    role_query = select(Role).where(Role.name == "org_admin")
    role_result = await db_session.execute(role_query)
    org_admin_role = role_result.scalar_one_or_none()
    
    assert org_admin_role is not None, "org_admin role should exist"
    
    # Assign org_admin role
    user_role = UserRole(
        user_id=org_admin_user.id,
        role_id=org_admin_role.id,
        organization_id=org_id
    )
    db_session.add(user_role)
    await db_session.commit()
    
    # Login as org_admin
    login_response = await client.post(
        "/api/v1/auth/access-token",
        data={"username": "org.admin@test.com", "password": "test123"}
    )
    assert login_response.status_code == 200
    org_admin_token = login_response.json()["access_token"]
    
    # Reload the user to ensure all relationships are loaded
    await db_session.refresh(org_admin_user)
    
    # Try to get organization users
    response = await client.get(
        f"/api/v1/users/organization/{org_id}/users",
        headers={"Authorization": f"Bearer {org_admin_token}"}
    )
    
    # Debug: Print response if not 200
    if response.status_code != 200:
        print(f"\n❌ Response status: {response.status_code}")
        print(f"Response body: {response.text}")
        print(f"Org ID: {org_id}")
    
    # org_admin should now be able to access their organization's users
    assert response.status_code == 200
    assert isinstance(response.json(), list)


@pytest.mark.asyncio
async def test_org_admin_cannot_view_other_organization_users(
    client: AsyncClient,
    db_session: AsyncSession,
    test_organization: Organization,
):
    """Test that org_admin cannot view users from other organizations."""
    # Create another organization
    other_org = Organization(
        name="Other Organization",
        created_by=test_organization.created_by,
        updated_by=test_organization.updated_by,
        is_active=True,
        is_deleted=False,
    )
    db_session.add(other_org)
    await db_session.commit()
    await db_session.refresh(other_org)
    
    # Create org_admin for test_organization
    org_admin_user = User(
        email="my.org.admin@test.com",
        hashed_password=get_password_hash("test123"),
        is_active=True,
        organization_id=test_organization.id,
        role="user"
    )
    db_session.add(org_admin_user)
    await db_session.commit()
    await db_session.refresh(org_admin_user)
    
    # Add to organization
    await db_session.execute(
        user_organization.insert().values(
            user_id=org_admin_user.id,
            organization_id=test_organization.id
        )
    )
    await db_session.commit()
    
    # Get org_admin role
    role_query = select(Role).where(Role.name == "org_admin")
    role_result = await db_session.execute(role_query)
    org_admin_role = role_result.scalar_one_or_none()
    
    # Assign org_admin role for test_organization
    user_role = UserRole(
        user_id=org_admin_user.id,
        role_id=org_admin_role.id,
        organization_id=test_organization.id
    )
    db_session.add(user_role)
    await db_session.commit()
    
    # Login as org_admin
    login_response = await client.post(
        "/api/v1/auth/access-token",
        data={"username": "my.org.admin@test.com", "password": "test123"}
    )
    assert login_response.status_code == 200
    org_admin_token = login_response.json()["access_token"]
    
    # Try to get users from OTHER organization
    response = await client.get(
        f"/api/v1/users/organization/{other_org.id}/users",
        headers={"Authorization": f"Bearer {org_admin_token}"}
    )
    
    # Should be forbidden
    assert response.status_code == 403
    assert "Not enough permissions" in response.json()["detail"]