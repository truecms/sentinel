"""
Tests for user delete operations.
"""

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_password_hash
from app.models.user import User

pytestmark = pytest.mark.asyncio


async def test_delete_user(
    client: AsyncClient, superuser_token_headers: dict, db_session: AsyncSession
):
    """Test deleting a user."""
    # Create user to delete
    user = User(
        email="todelete@example.com",
        hashed_password=get_password_hash("testpass123"),
        is_active=True,
        role="user",
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    response = await client.delete(
        f"/api/v1/users/{user.id}", headers=superuser_token_headers
    )
    assert response.status_code == 200

    # Verify user is deleted
    response = await client.get(
        f"/api/v1/users/{user.id}", headers=superuser_token_headers
    )
    assert response.status_code == 404


async def test_delete_user_not_found(
    client: AsyncClient, superuser_token_headers: dict
):
    """Test deleting a non-existent user."""
    response = await client.delete(
        "/api/v1/users/99999", headers=superuser_token_headers  # Non-existent user ID
    )
    assert response.status_code == 404


async def test_delete_user_unauthorized(
    client: AsyncClient, user_token_headers: dict, test_user: User
):
    """Test deleting a user without proper permissions."""
    response = await client.delete(
        f"/api/v1/users/{test_user.id}", headers=user_token_headers
    )
    assert response.status_code == 403


async def test_delete_superuser(
    client: AsyncClient, superuser_token_headers: dict, test_superuser: User
):
    """Test attempting to delete a superuser."""
    response = await client.delete(
        f"/api/v1/users/{test_superuser.id}", headers=superuser_token_headers
    )
    assert response.status_code == 400
    assert "Cannot delete superuser" in response.json()["detail"]


async def test_delete_organization_admin(
    client: AsyncClient, superuser_token_headers: dict, test_admin_user: User
):
    """Test deleting an organization admin."""
    response = await client.delete(
        f"/api/v1/users/{test_admin_user.id}", headers=superuser_token_headers
    )
    assert response.status_code == 200

    # Verify admin is deleted
    response = await client.get(
        f"/api/v1/users/{test_admin_user.id}", headers=superuser_token_headers
    )
    assert response.status_code == 404
