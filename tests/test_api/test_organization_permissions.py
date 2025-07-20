"""Test organization permissions using RBAC"""
import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.security import get_password_hash, create_access_token
from app.models.organization import Organization
from app.models.role import Role, UserRole
from app.models.user import User
from app.models.user_organization import user_organization


@pytest.mark.asyncio
async def test_org_admin_can_update_organization(
    client: AsyncClient,
    db_session: AsyncSession,
    test_organization: Organization
):
    """Test that org_admin can update their organization"""
    # Create a user with proper password hash
    user = User(
        email="orgadmin@example.com",
        full_name="Org Admin",
        hashed_password=get_password_hash("test123"),
        is_active=True,
        organization_id=test_organization.id
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    
    # Add user-organization association
    await db_session.execute(
        user_organization.insert().values(
            user_id=user.id,
            organization_id=test_organization.id,
            is_default=True
        )
    )
    await db_session.commit()
    
    # Assign org_admin role
    role_query = select(Role).where(Role.name == "org_admin")
    result = await db_session.execute(role_query)
    org_admin_role = result.scalar_one_or_none()
    
    assert org_admin_role is not None, "org_admin role should exist"
    
    user_role = UserRole.assign_role(
        user_id=user.id,
        role_id=org_admin_role.id,
        organization_id=test_organization.id,
        assigned_by_id=user.id
    )
    db_session.add(user_role)
    await db_session.commit()
    
    # Login as org_admin
    response = await client.post(
        "/api/v1/auth/access-token",
        data={"username": "orgadmin@example.com", "password": "test123"}
    )
    assert response.status_code == 200
    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Try to update the organization
    update_data = {
        "name": "Updated Organization Name",
        "description": "Updated description"
    }
    
    response = await client.put(
        f"/api/v1/organizations/{test_organization.id}",
        json=update_data,
        headers=headers
    )
    
    # Should succeed if permissions are working
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Updated Organization Name"
    assert data["description"] == "Updated description"


@pytest.mark.asyncio
async def test_non_org_admin_cannot_update_organization(
    client: AsyncClient,
    db_session: AsyncSession,
    test_organization: Organization
):
    """Test that non-org_admin users cannot update organizations"""
    # Create a regular user
    user = User(
        email="regular@example.com",
        full_name="Regular User",
        hashed_password=get_password_hash("test123"),
        is_active=True,
        organization_id=test_organization.id
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    
    # Add user-organization association
    await db_session.execute(
        user_organization.insert().values(
            user_id=user.id,
            organization_id=test_organization.id,
            is_default=True
        )
    )
    await db_session.commit()
    
    # Login as regular user
    response = await client.post(
        "/api/v1/auth/access-token",
        data={"username": "regular@example.com", "password": "test123"}
    )
    assert response.status_code == 200
    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Try to update the organization
    update_data = {
        "name": "Should Not Update",
        "description": "Should not be updated"
    }
    
    response = await client.put(
        f"/api/v1/organizations/{test_organization.id}",
        json=update_data,
        headers=headers
    )
    
    # Should fail with 403 Forbidden
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_org_admin_can_delete_own_organization(
    client: AsyncClient,
    db_session: AsyncSession,
    test_organization: Organization
):
    """Test that org_admin can delete their organization"""
    # Create a user with org_admin role
    user = User(
        email="orgadmin2@example.com",
        full_name="Org Admin 2",
        hashed_password=get_password_hash("test123"),
        is_active=True,
        organization_id=test_organization.id
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    
    # Add user-organization association
    await db_session.execute(
        user_organization.insert().values(
            user_id=user.id,
            organization_id=test_organization.id,
            is_default=True
        )
    )
    await db_session.commit()
    
    # Assign org_admin role
    role_query = select(Role).where(Role.name == "org_admin")
    result = await db_session.execute(role_query)
    org_admin_role = result.scalar_one_or_none()
    
    user_role = UserRole.assign_role(
        user_id=user.id,
        role_id=org_admin_role.id,
        organization_id=test_organization.id,
        assigned_by_id=user.id
    )
    db_session.add(user_role)
    await db_session.commit()
    
    # Login as org_admin
    response = await client.post(
        "/api/v1/auth/access-token",
        data={"username": "orgadmin2@example.com", "password": "test123"}
    )
    assert response.status_code == 200
    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Try to delete the organization
    response = await client.delete(
        f"/api/v1/organizations/{test_organization.id}",
        headers=headers
    )
    
    # Should succeed if permissions are working
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Organization deleted successfully"
    assert data["organization_id"] == test_organization.id


@pytest.mark.asyncio
async def test_org_admin_cannot_access_other_organizations(
    client: AsyncClient,
    db_session: AsyncSession,
    test_organization: Organization,
    test_user: User
):
    """Test that org_admin cannot access organizations they don't belong to"""
    # Create another organization
    other_org = Organization(
        name="Other Organization",
        created_by=test_user.id,
        updated_by=test_user.id,
        is_active=True,
        is_deleted=False,
    )
    db_session.add(other_org)
    await db_session.commit()
    await db_session.refresh(other_org)
    
    # Create org_admin user for test_organization
    user = User(
        email="orgadmin3@example.com",
        full_name="Org Admin 3",
        hashed_password=get_password_hash("test123"),
        is_active=True,
        organization_id=test_organization.id
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    
    # Add user-organization association
    await db_session.execute(
        user_organization.insert().values(
            user_id=user.id,
            organization_id=test_organization.id,
            is_default=True
        )
    )
    await db_session.commit()
    
    # Assign org_admin role
    role_query = select(Role).where(Role.name == "org_admin")
    result = await db_session.execute(role_query)
    org_admin_role = result.scalar_one_or_none()
    
    user_role = UserRole.assign_role(
        user_id=user.id,
        role_id=org_admin_role.id,
        organization_id=test_organization.id,
        assigned_by_id=user.id
    )
    db_session.add(user_role)
    await db_session.commit()
    
    # Login as org_admin
    response = await client.post(
        "/api/v1/auth/access-token",
        data={"username": "orgadmin3@example.com", "password": "test123"}
    )
    assert response.status_code == 200
    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Try to update the OTHER organization
    update_data = {
        "name": "Hacked Organization",
        "description": "Should not be allowed"
    }
    
    response = await client.put(
        f"/api/v1/organizations/{other_org.id}",
        json=update_data,
        headers=headers
    )
    
    # Should fail with 403 Forbidden
    assert response.status_code == 403
    
    # Try to delete the OTHER organization
    response = await client.delete(
        f"/api/v1/organizations/{other_org.id}",
        headers=headers
    )
    
    # Should fail with 403 Forbidden
    assert response.status_code == 403