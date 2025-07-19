"""
Tests for user active status filtering.
"""

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_password_hash
from app.models.user import User

pytestmark = pytest.mark.asyncio


async def test_get_users_filter_active(
    client: AsyncClient, superuser_token_headers: dict, db_session: AsyncSession
):
    """Test filtering users by active status."""
    # Create active and inactive users
    active_user = User(
        email="active@example.com",
        hashed_password=get_password_hash("testpass123"),
        is_active=True,
        role="user",
    )
    inactive_user = User(
        email="inactive@example.com",
        hashed_password=get_password_hash("testpass123"),
        is_active=False,
        role="user",
    )
    db_session.add(active_user)
    db_session.add(inactive_user)
    await db_session.commit()

    # Test filtering active users
    response = await client.get(
        "/api/v1/users/?is_active=true", headers=superuser_token_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert all(user["is_active"] for user in data)

    # Test filtering inactive users
    response = await client.get(
        "/api/v1/users/?is_active=false", headers=superuser_token_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert all(not user["is_active"] for user in data)