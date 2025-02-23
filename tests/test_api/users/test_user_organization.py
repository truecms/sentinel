"""
Tests for user organization operations.
"""

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User
from app.models.organization import Organization
from app.core.security import get_password_hash
from app.models.user_organization import user_organization
from sqlalchemy import select

pytestmark = pytest.mark.asyncio

async def test_create_user_with_organization(
    client: AsyncClient,
    superuser_token_headers: dict,
    test_organization: Organization,
    db_session: AsyncSession
):
    """Test creating a user with organization assignment."""
    # Store organization ID before async operation
    org_id = test_organization.id
    
    response = await client.post(
        "/api/v1/users/",
        headers=superuser_token_headers,
        json={
            "email": "neworguser@example.com",
            "password": "testpass123",
            "organization_id": org_id,
            "role": "user",
            "is_active": True,
            "is_superuser": False
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["organization_id"] == org_id

    # Verify user-organization association
    result = await db_session.execute(
        select(user_organization).where(
            user_organization.c.user_id == data["id"],
            user_organization.c.organization_id == org_id
        )
    )
    association = result.first()
    assert association is not None

async def test_create_user_invalid_organization(
    client: AsyncClient,
    superuser_token_headers: dict
):
    """Test creating a user with invalid organization ID."""
    response = await client.post(
        "/api/v1/users/",
        headers=superuser_token_headers,
        json={
            "email": "invalid@example.com",
            "password": "testpass123",
            "organization_id": 99999,  # Non-existent organization ID
            "role": "user",
            "is_active": True,
            "is_superuser": False
        }
    )
    assert response.status_code == 404
    assert "Organization not found" in response.json()["detail"]

async def test_update_user_organization(
    client: AsyncClient,
    superuser_token_headers: dict,
    test_user: User,
    test_organization: Organization,
    db_session: AsyncSession
):
    """Test updating user's organization."""
    # Store IDs before async operation
    user_id = test_user.id
    org_id = test_organization.id
    
    response = await client.put(
        f"/api/v1/users/{user_id}",
        headers=superuser_token_headers,
        json={
            "email": test_user.email,
            "organization_id": org_id
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["organization_id"] == org_id

    # Verify user-organization association
    result = await db_session.execute(
        select(user_organization).where(
            user_organization.c.user_id == user_id,
            user_organization.c.organization_id == org_id
        )
    )
    association = result.first()
    assert association is not None

async def test_get_organization_users(
    client: AsyncClient,
    superuser_token_headers: dict,
    test_organization: Organization,
    test_user: User,
    db_session: AsyncSession
):
    """Test getting all users in an organization."""
    # Store IDs before async operation
    org_id = test_organization.id
    
    # Create additional users in the organization
    for i in range(2):
        user = User(
            email=f"orguser{i}@example.com",
            hashed_password=get_password_hash("testpass123"),
            is_active=True,
            organization_id=org_id,
            role="user"
        )
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)

        # Add user-organization association
        await db_session.execute(
            user_organization.insert().values(
                user_id=user.id,
                organization_id=org_id
            )
        )
        await db_session.commit()

    # Add test_user to the organization
    await db_session.execute(
        user_organization.insert().values(
            user_id=test_user.id,
            organization_id=org_id
        )
    )
    await db_session.commit()

    response = await client.get(
        f"/api/v1/users/organization/{org_id}/users",
        headers=superuser_token_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 3  # test_user + 2 new users

async def test_get_organization_users_not_found(
    client: AsyncClient,
    superuser_token_headers: dict
):
    """Test getting users from non-existent organization."""
    response = await client.get(
        "/api/v1/users/organization/99999/users",  # Non-existent organization ID
        headers=superuser_token_headers
    )
    assert response.status_code == 404
    assert "Organization not found" in response.json()["detail"]

async def test_get_organization_users_empty(
    client: AsyncClient,
    superuser_token_headers: dict,
    test_organization: Organization
):
    """Test getting users from an empty organization."""
    response = await client.get(
        f"/api/v1/users/organization/{test_organization.id}/users",
        headers=superuser_token_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 0 