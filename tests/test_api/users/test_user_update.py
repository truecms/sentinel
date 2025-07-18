"""
Tests for user update operations.
"""

import pytest
from httpx import AsyncClient

from app.models.organization import Organization
from app.models.user import User

_ = pytest.mark.asyncio


async def test_update_user(
    client: AsyncClient, superuser_token_headers: dict, test_user: User
):
    """Test updating user details."""
    # Store user ID before async operation
    user_id = test_user.id

    response = await client.put(
        f"/api/v1/users/{user_id}",
        headers=superuser_token_headers,
        json={"email": "updated@example.com", "is_active": True},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "updated@example.com"
    assert data["id"] == user_id


async def test_update_user_role(
    client: AsyncClient, superuser_token_headers: dict, test_user: User
):
    """Test updating user role."""
    response = await client.put(
        f"/api/v1/users/{test_user.id}",
        headers=superuser_token_headers,
        json={"email": test_user.email, "role": "admin"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["role"] == "admin"


async def test_update_user_organization(
    client: AsyncClient,
    superuser_token_headers: dict,
    test_user: User,
    test_organization: Organization,
):
    """Test updating user organization."""
    # Store IDs before async operation
    user_id = test_user.id
    org_id = test_organization.id

    response = await client.put(
        f"/api/v1/users/{user_id}",
        headers=superuser_token_headers,
        json={"email": test_user.email, "organization_id": org_id},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["organization_id"] == org_id


async def test_update_user_multiple_fields(
    client: AsyncClient,
    superuser_token_headers: dict,
    test_user: User,
    test_organization: Organization,
):
    """Test updating multiple user fields at once."""
    # Store IDs before async operation
    user_id = test_user.id
    org_id = test_organization.id

    response = await client.put(
        f"/api/v1/users/{user_id}",
        headers=superuser_token_headers,
        json={
            "email": "multi@example.com",
            "role": "admin",
            "organization_id": org_id,
            "is_active": True,
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "multi@example.com"
    assert data["role"] == "admin"
    assert data["organization_id"] == org_id
    assert data["is_active"] is True


async def test_update_user_not_found(
    client: AsyncClient, superuser_token_headers: dict
):
    """Test updating a non-existent user."""
    response = await client.put(
        "/api/v1/users/99999",  # Non-existent user ID
        headers=superuser_token_headers,
        json={"email": "notfound@example.com", "is_active": True},
    )
    assert response.status_code == 404


async def test_deactivate_user(
    client: AsyncClient, superuser_token_headers: dict, test_user: User
):
    """Test deactivating a user."""
    response = await client.put(
        f"/api/v1/users/{test_user.id}",
        _=superuser_token_headers,
        json={"email": test_user.email, "is_active": False},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["is_active"] is False
