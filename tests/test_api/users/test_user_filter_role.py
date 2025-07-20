"""
Tests for user role filtering.
"""

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_password_hash
from app.models.user import User

pytestmark = pytest.mark.asyncio


async def test_get_users_filter_role(
    client: AsyncClient, superuser_token_headers: dict, db_session: AsyncSession
):
    """Test filtering users by role."""
    # Create users with different roles
    admin_user = User(
        email="admin_role_test@example.com",
        hashed_password=get_password_hash("testpass123"),
        is_active=True,
        role="admin",
    )
    regular_user = User(
        email="user@example.com",
        hashed_password=get_password_hash("testpass123"),
        is_active=True,
        role="user",
    )
    db_session.add(admin_user)
    db_session.add(regular_user)
    await db_session.commit()

    # Test filtering admin users
    response = await client.get(
        "/api/v1/users/?role=admin", headers=superuser_token_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert all(user["role"] == "admin" for user in data)

    # Test filtering regular users
    response = await client.get(
        "/api/v1/users/?role=user", headers=superuser_token_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert all(user["role"] == "user" for user in data)