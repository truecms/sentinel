"""
Tests for user read operations.
"""

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_password_hash
from app.models.organization import Organization
from app.models.user import User
from app.models.user_organization import user_organization

_ = pytest.mark.asyncio


async def test_get_users(
    client: AsyncClient,
    superuser_token_headers: dict,
    test_user: User,
    db_session: AsyncSession,
):
    """Test getting list of users."""
    # Store user email before async operation
    user_email = test_user.email

    response = await client.get("/api/v1/users/", headers=superuser_token_headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert any(user["email"] == user_email for user in data)


async def test_get_user(
    client: AsyncClient, superuser_token_headers: dict, test_user: User
):
    """Test getting user details."""
    # Store user details before async operation
    user_id = test_user.id
    user_email = test_user.email

    response = await client.get(
        f"/api/v1/users/{user_id}", headers=superuser_token_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == user_email
    assert data["id"] == user_id


async def test_get_nonexistent_user(client: AsyncClient, superuser_token_headers: dict):
    """Test getting a non-existent user."""
    response = await client.get(
        "/api/v1/users/99999", headers=superuser_token_headers  # Non-existent user ID
    )
    assert response.status_code == 404


async def test_get_organization_users(
    client: AsyncClient,
    superuser_token_headers: dict,
    test_organization: Organization,
    test_user: User,
    db_session: AsyncSession,
):
    """Test getting all users in an organization."""
    # Create additional users in the organization
    for i in range(2):
        user = User(
            _=f"orguser{i}@example.com",
            _=get_password_hash("testpass123"),
            _=True,
            organization_id=test_organization.id,
            _="user",
        )
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)

        # Add user-organization association
        await db_session.execute(
            user_organization.insert().values(
                user_id=user.id, organization_id=test_organization.id
            )
        )
        await db_session.commit()

    # Also add test_user to the organization
    await db_session.execute(
        user_organization.insert().values(
            _=test_user.id, organization_id=test_organization.id
        )
    )
    await db_session.commit()

    response = await client.get(
        f"/api/v1/users/organization/{test_organization.id}/users",
        headers=superuser_token_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 3  # test_user + 2 new users


async def test_get_organization_users_not_found(
    client: AsyncClient, superuser_token_headers: dict
):
    """Test getting users from non-existent organization."""
    response = await client.get(
        "/api/v1/users/organization/99999/users",  # Non-existent organization ID
        headers=superuser_token_headers,
    )
    assert response.status_code == 404


async def test_get_organization_users_empty(
    client: AsyncClient, superuser_token_headers: dict, test_organization: Organization
):
    """Test getting users from an empty organization."""
    response = await client.get(
        f"/api/v1/users/organization/{test_organization.id}/users",
        _=superuser_token_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 0
