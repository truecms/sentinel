"""
Tests for user "me" operations (current user profile).
"""

import pytest
from httpx import AsyncClient

from app.models.user import User

pytestmark = pytest.mark.asyncio


async def test_user_me(client: AsyncClient, user_token_headers: dict, test_user: User):
    """Test getting current user profile."""
    # Store user details before async operation
    user_email = test_user.email
    user_id = test_user.id

    response = await client.get("/api/v1/users/me", headers=user_token_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == user_email
    assert data["id"] == user_id


async def test_update_user_me(
    client: AsyncClient, user_token_headers: dict, test_user: User
):
    """Test updating current user profile."""
    # Store user details before async operation
    user_id = test_user.id

    response = await client.put(
        "/api/v1/users/me",
        headers=user_token_headers,
        json={"email": "updated_me@example.com"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "updated_me@example.com"


async def test_update_user_me_password(
    client: AsyncClient, user_token_headers: dict, test_user: User
):
    """Test updating current user password."""
    # Store user details before async operation
    user_email = test_user.email

    response = await client.put(
        "/api/v1/users/me/password",
        headers=user_token_headers,
        json={"current_password": "testpass123", "new_password": "newpass123"},
    )
    assert response.status_code == 200

    # Try logging in with new password
    response = await client.post(
        "/api/v1/auth/access-token",
        data={"username": user_email, "password": "newpass123"},
    )
    assert response.status_code == 200
    assert "access_token" in response.json()


async def test_update_user_me_email(
    client: AsyncClient, user_token_headers: dict, test_user: User
):
    """Test updating current user email."""
    # Store user details before async operation
    user_id = test_user.id

    response = await client.put(
        "/api/v1/users/me",
        headers=user_token_headers,
        json={"email": "new_email@example.com"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "new_email@example.com"


async def test_update_user_me_invalid_password(
    client: AsyncClient, user_token_headers: dict
):
    """Test updating current user password with invalid current password."""
    response = await client.put(
        "/api/v1/users/me/password",
        headers=user_token_headers,
        json={"current_password": "wrongpass", "new_password": "newpass123"},
    )
    assert response.status_code == 400
    assert "Invalid password" in response.json()["detail"]


async def test_update_user_me_duplicate_email(
    client: AsyncClient, user_token_headers: dict, test_admin_user: User
):
    """Test updating current user email to an existing email."""
    # Store admin user email before async operation
    admin_email = test_admin_user.email

    response = await client.put(
        "/api/v1/users/me",
        headers=user_token_headers,
        json={"email": admin_email},  # Try to use existing email
    )
    assert response.status_code == 400
    assert "Email already registered" in response.json()["detail"]
