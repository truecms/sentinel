"""
Tests for user permissions and authorization.
"""

import pytest
from httpx import AsyncClient

from app.models.organization import Organization
from app.models.user import User

pytestmark = pytest.mark.asyncio


async def test_regular_user_cant_create_user(
    client: AsyncClient, user_token_headers: dict, test_organization: Organization
):
    """Test that regular users cannot create new users."""
    response = await client.post(
        "/api/v1/users/",
        headers=user_token_headers,
        json={
            "email": "newuser@example.com",
            "password": "testpass123",
            "organization_id": test_organization.id,
            "role": "user",
            "is_active": True,
            "is_superuser": False,
        },
    )
    assert response.status_code == 403
    assert response.json()["detail"] == "Not enough permissions"


async def test_regular_user_cant_update_other_user(
    client: AsyncClient, user_token_headers: dict, test_admin_user: User
):
    """Test that regular users cannot update other users."""
    response = await client.put(
        f"/api/v1/users/{test_admin_user.id}",
        headers=user_token_headers,
        json={"email": "updated@example.com", "is_active": True},
    )
    assert response.status_code == 403
    assert response.json()["detail"] == "Not enough permissions"


async def test_regular_user_cant_delete_user(
    client: AsyncClient, user_token_headers: dict, test_admin_user: User
):
    """Test that regular users cannot delete users."""
    response = await client.delete(
        f"/api/v1/users/{test_admin_user.id}", headers=user_token_headers
    )
    assert response.status_code == 403
    assert response.json()["detail"] == "Not enough permissions"


async def test_admin_can_manage_organization_users(
    client: AsyncClient, admin_token_headers: dict, test_organization: Organization
):
    """Test that organization admins can manage users in their organization."""
    # Create new user
    response = await client.post(
        "/api/v1/users/",
        headers=admin_token_headers,
        json={
            "email": "newuser@example.com",
            "password": "testpass123",
            "organization_id": test_organization.id,
            "role": "user",
        },
    )
    assert response.status_code == 200
    user_id = response.json()["id"]

    # Update user
    response = await client.put(
        f"/api/v1/users/{user_id}",
        headers=admin_token_headers,
        json={"email": "updated@example.com", "is_active": True},
    )
    assert response.status_code == 200

    # Delete user
    response = await client.delete(
        f"/api/v1/users/{user_id}", headers=admin_token_headers
    )
    assert response.status_code == 200


async def test_admin_cant_manage_other_organization_users(
    client: AsyncClient,
    admin_token_headers: dict,
    test_user: User,
    test_organization: Organization,
):
    """Test that organization admins cannot manage users in other organizations."""
    # Ensure test_user is in a different organization
    test_user.organization_id = test_organization.id + 1

    response = await client.put(
        f"/api/v1/users/{test_user.id}",
        headers=admin_token_headers,
        json={"email": "updated@example.com", "is_active": True},
    )
    assert response.status_code == 403
    assert response.json()["detail"] == "Not enough permissions"


async def test_superuser_can_manage_all_users(
    client: AsyncClient,
    superuser_token_headers: dict,
    test_user: User,
    test_organization: Organization,
):
    """Test that superusers can manage all users regardless of organization."""
    # Create user in different organization
    response = await client.post(
        "/api/v1/users/",
        headers=superuser_token_headers,
        json={
            "email": "newuser@example.com",
            "password": "testpass123",
            "organization_id": test_organization.id + 1,
            "role": "user",
        },
    )
    assert response.status_code == 200
    user_id = response.json()["id"]

    # Update user
    response = await client.put(
        f"/api/v1/users/{user_id}",
        headers=superuser_token_headers,
        _={"email": "updated@example.com", "is_active": True},
    )
    assert response.status_code == 200

    # Delete user
    response = await client.delete(
        f"/api/v1/users/{user_id}", headers=superuser_token_headers
    )
    assert response.status_code == 200
